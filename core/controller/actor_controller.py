import pprint
from asyncio import Future
import asyncio
from aiohttp import web

from core.api.actor import CBPiActor
from core.api.decorator import on_event, request_mapping
from core.controller.crud_controller import CRUDController
from core.database.model import ActorModel
from core.http_endpoints.http_api import HttpAPI
from core.utils import parse_props


class ActorHttp(HttpAPI):

    @request_mapping(path="/{id:\d+}/on", auth_required=False)
    async def http_on(self, request) -> web.Response:
        """
        :param request: 
        :return: 
        """
        id = int(request.match_info['id'])
        result = await self.cbpi.bus.fire2(topic="actor/%s/switch/on" % id, id=id, power=99)
        print(result.timeout)

        for key, value in result.results.items():
            print(key, value.result)
        return web.Response(status=204)


    @request_mapping(path="/{id:\d+}/off", auth_required=False)
    async def http_off(self, request) -> web.Response:
        """
        :param request: 
        :return: 
        """
        id = int(request.match_info['id'])
        await self.cbpi.bus.fire(topic="actor/%s/off" % id, id=id)
        return web.Response(status=204)

    @request_mapping(path="/{id:\d+}/toggle", auth_required=False)
    async def http_toggle(self, request) -> web.Response:
        """
        :param request: 
        :return: 
        """
        id = int(request.match_info['id'])
        print("ID", id)
        await self.cbpi.bus.fire(topic="actor/%s/toggle" % id, id=id)
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

    async def init(self):
        '''
        This method initializes all actors during startup. It creates actor instances
        
        :return: 
        '''
        await super(ActorController, self).init()

        for id, value in self.cache.items():
            await self._init_actor(value)

    async def _init_actor(self, actor):
        if actor.type in self.types:
            cfg = actor.config.copy()
            cfg.update(dict(cbpi=self.cbpi, id=id, name=actor.name))
            clazz = self.types[actor.type]["class"];

            self.cache[actor.id].instance = clazz(**cfg)
            self.cache[actor.id].instance.init()
            await self.cbpi.bus.fire(topic="actor/%s/initialized" % actor.id, id=actor.id)


    async def _stop_actor(self, actor):
        actor.instance.stop()
        await self.cbpi.bus.fire(topic="actor/%s/stopped" % actor.id, id=actor.id)



    @on_event(topic="actor/+/switch/on")
    async def on(self, id , future: Future, power=100,  **kwargs) -> None:
        '''
        Method to switch an actor on.
        Supporting Event Topic "actor/+/on"
        
        :param actor_id: the actor id
        :param power: as integer value between 1 and 100
        :param kwargs: 
        :return: 
        '''

        id = int(id)
        if id in self.cache:
            print("POWER ON")
            actor = self.cache[id   ].instance
            await self.cbpi.bus.fire("actor/%s/on/ok" % id)
            actor.on(power)

        future.set_result("OK")

    @on_event(topic="actor/+/toggle")
    async def toggle(self, id, power=100, **kwargs) -> None:
        '''
        Method to toggle an actor on or off
        Supporting Event Topic "actor/+/toggle"
        
        :param id: the actor id 
        :param power: the power as interger between 0 and 100
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
    async def off(self, id, **kwargs) -> None:
        """
        
        Method to switch and actor off
        Supporting Event Topic "actor/+/off"
        
        :param id: the actor id 
        :param kwargs: 
        """

        id = int(id)

        if id in self.cache:
            actor = self.cache[id].instance
            actor.off()

    async def _post_add_callback(self, m):
        '''
    
        :param m: 
        :return: 
        '''
        await self._init_actor(m)
        pass

    async def _pre_delete_callback(self, actor_id):
        if int(actor_id) not in self.cache:
            return

        if self.cache[int(actor_id)].instance is not None:
            await self._stop_actor(self.cache[int(actor_id)])

    async def _pre_update_callback(self, actor):

        if actor.instance is not None:
            await self._stop_actor(actor)

    async def _post_update_callback(self, actor):
        self._init_actor(actor)
