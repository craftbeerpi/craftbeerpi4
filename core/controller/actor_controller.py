from aiohttp import web
from aiohttp_auth.auth.decorators import auth_required

from core.api.decorator import on_event, request_mapping
from core.controller.crud_controller import CRUDController
from core.database.model import ActorModel
from core.http_endpoints.http_api import HttpAPI
from core.plugin import PluginAPI


class ActorController(HttpAPI, CRUDController, PluginAPI):


    model = ActorModel


    def __init__(self, cbpi):
        super(ActorController, self).__init__(cbpi)
        self.cbpi = cbpi
        self.state = False;

        self.cbpi.register(self, "/actor")
        self.types = {}
        self.actors = {}


    async def init(self):

        await super(ActorController, self).init()
        for name, clazz in self.types.items():
            print("Type", name)
        for id, value in self.cache.items():

            if value.type in self.types:
                clazz = self.types[value.type];
                self.actors[id]  = clazz(self.cbpi)
            print(value.type)
        print("CACHE", self.cache)
        print("ACTORS", self.actors)

    @request_mapping(path="/{id}/on",auth_required=False)
    async def http_on(self, request) -> web.Response:
        self.cbpi.bus.fire(event="actor/1/on", id=1, power=99)
        return web.Response(status=204)

    @on_event(topic="actor/+/on")
    def on(self, id, power=100) -> None:
        print("ON-------------", id, power)
        if id in self.actors:
            i = self.actors[id]
            i.on(power)

    @on_event(topic="actor/+/on")
    def on2(self, id, **kwargs) -> None:
        print("POWERED ON", id, kwargs)



    def register(self, name, clazz) -> None:
        '''
        Register a new actor type
        :param name: actor name
        :param clazz: actor class
        :return: None
        '''
        self._parse_props(clazz)
        self.types[name] = clazz




