from aiohttp import web

from core.api import request_mapping
from core.controller.crud_controller import CRUDController
from core.database.model import KettleModel
from core.http_endpoints.http_api import HttpAPI
from core.utils import json_dumps


class KettleHttp(HttpAPI):

    @request_mapping(path="/types", auth_required=False)
    async def get_types(self, request):
        web.json_response(data=self.types, dumps=json_dumps)

    @request_mapping(path="/automatic", auth_required=False)
    async def start(self, request):
        await self.toggle_automtic(1)
        return web.Response(text="OK")

    @request_mapping(path="/automatic/stop", auth_required=False)
    async def stop(self, request):
        kettle = await self.get_one(1)
        kettle.instance.running = False
        return web.Response(text="OK")



class KettleController(CRUDController, KettleHttp):
    '''
    The main actor controller
    '''
    model = KettleModel

    def __init__(self, cbpi):
        super(KettleController, self).__init__(cbpi)
        self.cbpi = cbpi
        self.types = {}
        self.cbpi.register(self, "/kettle")

    async def init(self):
        '''
        This method initializes all actors during startup. It creates actor instances

        :return: 
        '''
        await super(KettleController, self).init()

    async def toggle_automtic(self, id):
        kettle = await self.get_one(id)

        if hasattr(kettle, "instance") is False:
            kettle.instance = None

        if kettle.instance is None:
            if kettle.logic in self.types:
                clazz = self.types.get("CustomKettleLogic")["class"]
                kettle.instance = clazz()
                await self.cbpi.start_job(kettle.instance.run(), "test", "test")
        else:
            kettle.instance.running = False
            kettle.instance = None


    async def heater_on(self, id):
        pass

    async def heater_off(self, id):
        pass

    async def agitator_on(self, id):
        pass

    async def agitator_off(self, id):
        pass

    async def get_traget_temp(self, id):
        pass

    async def get_temp(self, id):
        pass
