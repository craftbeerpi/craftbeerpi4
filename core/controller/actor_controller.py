from aiohttp import web

from core.api.actor import CBPiActor
from core.api.decorator import on_event, request_mapping
from core.controller.crud_controller import CRUDController
from core.database.model import ActorModel
from core.http_endpoints.http_api import HttpAPI
from core.utils import parse_props


class ActorHttp(HttpAPI):

    @request_mapping(path="/{id}/on", auth_required=False)
    async def http_on(self, request) -> web.Response:
        """
        :param request: 
        :return: 
        """
        id = int(request.match_info['id'])
        self.cbpi.bus.fire(topic="actor/%s/on" % id, id=id, power=99)
        return web.Response(status=204)


    @request_mapping(path="/{id}/off", auth_required=False)
    async def http_off(self, request) -> web.Response:
        """
        :param request: 
        :return: 
        """
        id = int(request.match_info['id'])
        self.cbpi.bus.fire(topic="actor/%s/off" % id, id=id)
        return web.Response(status=204)

    @request_mapping(path="/{id}/toggle", auth_required=False)
    async def http_toggle(self, request) -> web.Response:
        """
        :param request: 
        :return: 
        """
        id = int(request.match_info['id'])
        print("ID", id)
        self.cbpi.bus.fire(topic="actor/%s/toggle" % id, id=id)
        return web.Response(status=204)

class ActorController(ActorHttp, CRUDController):

    '''
    The main actor controller
    '''
    model = ActorModel

    def __init__(self, cbpi):
        super(ActorController, self).__init__(cbpi)
        self.cbpi = cbpi
        self.state = False;

        self.cbpi.register(self, "/actor")
        self.types = {}
        self.actors = {}


    def register(self, name, clazz) -> None:

        print("REGISTER", name)
        if issubclass(clazz, CBPiActor):
            print("ITS AN ACTOR")

        parse_props(clazz)
        self.types[name] = clazz

    async def init(self):
        '''
        This method initializes all actors during startup. It creates actor instances
        
        :return: 
        '''
        await super(ActorController, self).init()

        for name, clazz in self.types.items():
            print("Type", name)

        for id, value in self.cache.items():

            if value.type in self.types:
                cfg = value.config.copy()
                print(cfg)
                cfg.update(dict(cbpi=self.cbpi, id=id, name=value.name))
                clazz = self.types[value.type]["class"];

                self.cache[id].instance = clazz(**cfg)
                print("gpIO", self.cache[id].instance, self.cache[id].instance.gpio)



    @on_event(topic="actor/+/on")
    def on(self, id, power=100, **kwargs) -> None:
        '''
        Method to switch an actor on.
        Supporting Event Topic "actor/+/on"
        
        :param id: the actor id
        :param power: as integer value between 1 and 100
        :param kwargs: 
        :return: 
        '''

        id = int(id)
        if id in self.cache:
            print("POWER ON")
            actor = self.cache[id].instance
            print("ONNNNN", actor)
            actor.on(power)

    @on_event(topic="actor/+/toggle")
    def toggle(self, id, power=100, **kwargs) -> None:
        '''
        Method to toggle an actor on or off
        Supporting Event Topic "actor/+/toggle"
        
        :param power: 
        :return: 
        '''

        id = int(id)
        if id in self.cache:
            actor = self.cache[id].instance
            if actor.state is True:
                actor.off()
            else:
                actor.on()

    @on_event(topic="actor/+/off")
    def off(self, id, **kwargs) -> None:
        """
        
        Method to switch and actor off
        Supporting Event Topic "actor/+/off"
        
        :param id: 
        :param kwargs: 
        """

        id = int(id)

        if id in self.cache:
            actor = self.cache[id].instance
            actor.off()
