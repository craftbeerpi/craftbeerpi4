import re


from cbpi_api import *
from cbpi_api.exceptions import KettleException, ActorException, SensorException

from core.controller.crud_controller import CRUDController
from core.database.model import KettleModel

from core.job.aiohttp import get_scheduler_from_app


class KettleController(CRUDController):
    '''
    The main kettle controller
    '''
    model = KettleModel

    def __init__(self, cbpi):
        super(KettleController, self).__init__(cbpi)
        self.cbpi = cbpi
        self.types = {}
        self.cbpi.register(self)

    async def init(self):
        '''
        This method initializes all actors during startup. It creates actor instances

        :return: 
        '''
        await super(KettleController, self).init()

    def get_state(self):
        return dict(items=self.cache,types=self.types)

    async def toggle_automtic(self, id):
        '''
        
        Convenience Method to toggle automatic
        
        :param id: kettle id as int
        :return: (boolean, string) 
        '''
        kettle = await self.get_one(id)
        if kettle is None:
            raise KettleException("Kettle not found")
        if kettle.logic is None:
            raise CBPiExtension("Logic not found for kettle id: %s" % id)

        await self.cbpi.bus.fire(topic="kettle/%s/automatic" % id, id=id)

    @on_event(topic="job/done")
    async def job_stop(self, key, **kwargs) -> None:

        match = re.match("kettle_logic_(\d+)", key)
        if match is not None:
            kid = match.group(1)
            kettle = self.cache[int(kid)]
            kettle.instance = None

    @on_event(topic="kettle/+/automatic")
    async def handle_automtic_event(self, id, **kwargs):

        '''
        Method to handle the event 'kettle/+/automatic'
        
        :param id: The kettle id
        :param kwargs: 
        :return: None
        '''
        id = int(id)

        if id in self.cache:

            kettle = self.cache[id]

            if hasattr(kettle, "instance") is False:
                kettle.instance = None
            self._is_logic_running(id)
            if kettle.instance is None:
                if kettle.logic in self.types:
                    clazz = self.types.get("CustomKettleLogic")["class"]
                    cfg = kettle.config.copy()
                    cfg.update(dict(cbpi=self.cbpi))
                    kettle.instance = clazz(**cfg)

                await self.cbpi.job.start_job(kettle.instance.run(), "Kettle_logic_%s" % kettle.id, "kettle_logic%s" % id)
            else:
                kettle.instance.running = False
                kettle.instance = None

    def _is_logic_running(self, kettle_id):
        scheduler = get_scheduler_from_app(self.cbpi.app)

    async def heater_on(self, id):
        '''
        Convenience Method to switch the heater of a kettle on
        
        
        :param id: the kettle id
        :return: (boolean, string) 
        '''
        kettle = await self.get_one(id)
        if kettle is None:
            raise KettleException("Kettle not found")
        if kettle.sensor is None:
            raise ActorException("Actor not defined for kettle id %s" % id)
        heater_id = kettle.heater
        await self.cbpi.bus.fire(topic="actor/%s/switch/on" % heater_id, actor_id=heater_id, power=99)

    async def heater_off(self, id):
        '''
        
        Convenience Method to switch the heater of a kettle off
        
        :param id: 
        :return: 
        '''
        kettle = await self.get_one(id)
        if kettle is None:
            raise KettleException("Kettle not found")
        if kettle.sensor is None:
            raise ActorException("Actor not defined for kettle id %s" % id)
        heater_id = kettle.heater
        await self.cbpi.bus.fire(topic="actor/%s/switch/off" % heater_id, actor_id=heater_id, power=99)

    async def agitator_on(self, id):
        kettle = await self.get_one(id)
        if kettle is None:
            raise KettleException("Kettle not found")
        if kettle.sensor is None:
            raise ActorException("Actor not defined for kettle id %s" % id)
        agitator_id = kettle.agitator
        await self.cbpi.bus.fire(topic="actor/%s/switch/on" % agitator_id, actor_id=agitator_id, power=99)

    async def agitator_off(self, id):
        kettle = await self.get_one(id)
        if kettle is None:
            raise KettleException("Kettle not found")
        if kettle.sensor is None:
            raise ActorException("Actor not defined for kettle id %s" % id)
        agitator_id = kettle.agitator
        await self.cbpi.bus.fire(topic="actor/%s/switch/off" % agitator_id, actor_id=agitator_id, power=99)

    async def get_traget_temp(self, id):
        kettle = await self.get_one(id)
        if kettle is None:
            raise KettleException("Kettle Not Found")
        return kettle.target_temp

    async def get_temp(self, id):

        kettle = await self.get_one(id)
        if kettle is None:
            raise KettleException("Kettle Not Found")
        if kettle.sensor is None:
            raise SensorException("Sensor not defined for kettle id %s" % id)

        sensor_id = kettle.sensor

        return await self.cbpi.sensor.get_value(sensor_id)
