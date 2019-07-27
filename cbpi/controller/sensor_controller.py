
import logging
from cbpi.controller.crud_controller import CRUDController
from cbpi.database.model import SensorModel
from cbpi.job.aiohttp import get_scheduler_from_app



class SensorController(CRUDController):

    model = SensorModel

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.cbpi.register(self)
        self.service = self
        self.types = {}
        self.logger = logging.getLogger(__name__)
        self.sensors = {}

    async def init(self):
        '''
        This method initializes all actors during startup. It creates actor instances

        :return: 
        '''


        await super(SensorController, self).init()
        for id, value in self.cache.items():
            await self.init_sensor(value)

    def get_state(self):
        return dict(items=self.cache,types=self.types)

    async def init_sensor(self, sensor):
        if sensor.type in self.types:
            cfg = sensor.config.copy()
            cfg.update(dict(cbpi=self.cbpi, id=sensor.id, name=sensor.name))
            clazz = self.types[sensor.type]["class"];
            self.cache[sensor.id].instance = clazz(**cfg)
            self.cache[sensor.id].instance.init()
            scheduler = get_scheduler_from_app(self.cbpi.app)

            self.cache[sensor.id].instance.job = await self.cbpi.job.start_job(self.cache[sensor.id].instance.run(self.cbpi), sensor.name, "sensor")

            await self.cbpi.bus.fire(topic="sensor/%s/initialized" % sensor.id, id=sensor.id)
        else:
            self.logger.error("Sensor type '%s' not found (Available Sensor Types: %s)" % (sensor.type, ', '.join(self.types.keys())))



    async def stop_sensor(self, sensor):

        sensor.instance.stop()
        await self.cbpi.bus.fire(topic="sensor/%s/stopped" % sensor.id, id=sensor.id)


    async def get_value(self, sensor_id):
        sensor_id = int(sensor_id)
        return self.cache[sensor_id].instance.value

    async def _post_add_callback(self, m):
        '''

        :param m:
        :return:
        '''
        await self.init_sensor(m)
        pass

    async def _pre_delete_callback(self, sensor_id):
        if int(sensor_id) not in self.cache:
            return
        if self.cache[int(sensor_id)].instance is not None:
            await self.stop_sensor(self.cache[int(sensor_id)])

    async def _pre_update_callback(self, sensor):

        if sensor.instance is not None:
            await self.stop_sensor(sensor)

    async def _post_update_callback(self, sensor):
        await self.init_sensor(sensor)