import re

from aiohttp import web


from cbpi_api import *
from core.controller.crud_controller import CRUDController
from core.database.model import KettleModel
from core.http_endpoints.http_api import HttpAPI
from core.job.aiohttp import get_scheduler_from_app
from core.utils import json_dumps


class KettleHttp(HttpAPI):

    @request_mapping(path="/types", auth_required=False)
    async def get_types(self, request):
        web.json_response(data=self.cbpi.kettle.types, dumps=json_dumps)

    @request_mapping(path="/{id:\d+}/automatic", auth_required=False)
    async def start2(self, request):
        id = int(request.match_info['id'])
        result = await self.cbpi.kettle.toggle_automtic(id)
        if result[0] is True:
            return web.Response(text="OK")
        else:
            return web.Response(status=404, text=result[1])

    @request_mapping(path="/{id:\d+}/heater", auth_required=False)
    async def start(self, request):
        id = int(request.match_info['id'])
        result = await self.cbpi.kettle.heater_on(id)
        if  result[0] is True:
            return web.Response(text="OK")
        else:
            return web.Response(status=404, text=result[1])

class KettleController(CRUDController):
    '''
    The main kettle controller
    '''
    model = KettleModel

    def __init__(self, cbpi):
        super(KettleController, self).__init__(cbpi)
        self.cbpi = cbpi
        self.types = {}
        self.cbpi.register(self, None)
        self.http = KettleHttp(cbpi)
        self.cbpi.register(self.http, "/kettle")



    async def init(self):
        '''
        This method initializes all actors during startup. It creates actor instances

        :return: 
        '''
        await super(KettleController, self).init()

    async def toggle_automtic(self, id):
        '''
        
        Convenience Method to toggle automatic
        
        :param id: kettle id as int
        :return: (boolean, string) 
        '''
        kettle = await self.get_one(id)
        if kettle is None:
            return (False, "Kettle Not Found")
        if kettle.logic is None:
            return (False, "No Logic defined")
        id = kettle.heater
        await self.cbpi.bus.fire(topic="kettle/%s/automatic" % id, id=id)
        return (True, "Logic switched on switched")

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

                await self.cbpi.start_job(kettle.instance.run(), "Kettle_logic_%s" % kettle.id, "kettle_logic%s"%id)
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
            return (False, "Kettle Not Found")
        if kettle.heater is None:
            return (False, "No Heater defined")
        id = kettle.heater
        await self.cbpi.bus.fire(topic="actor/%s/on" % id, id=id, power=99)
        return (True,"Heater switched on")

    async def heater_off(self, id):
        '''
        
        Convenience Method to switch the heater of a kettle off
        
        :param id: 
        :return: 
        '''
        kettle = await self.get_one(id)
        if kettle is None:
            return (False, "Kettle Not Found")
        if kettle.heater is None:
            return (False, "No Heater defined")
        id = kettle.heater
        await self.cbpi.bus.fire(topic="actor/%s/off" % id, id=id, power=99)
        return (True, "Heater switched off")

    async def agitator_on(self, id):
        pass

    async def agitator_off(self, id):
        pass

    async def get_traget_temp(self, id):
        kettle = await self.get_one(id)
        return kettle.target_temp

    async def get_temp(self, id):

        pass