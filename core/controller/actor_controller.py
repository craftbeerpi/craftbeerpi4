import json
import logging
from asyncio import Future

from aiohttp import web
from cbpi_api import *
from core.controller.crud_controller import CRUDController
from core.database.model import ActorModel
from core.http_endpoints.http_api import HttpAPI
from utils.encoder import ComplexEncoder

auth = False

class ActorHttp(HttpAPI):

    @request_mapping(path="/types", auth_required=False)
    async def get_types(self, request):
        """
        ---
        description: Get all actor types
        tags:
        - Actor
        responses:
            "200":
                description: successful operation
        """
        return await super().get_types(request)

    @request_mapping(path="/", auth_required=False)
    async def http_get_all(self, request):
        """

        ---
        description: Switch actor on
        tags:
        - Actor
        parameters:
        - name: "id"
          in: "path"
          description: "Actor ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
            "405":
                description: invalid HTTP Met
        """
        return await super().http_get_all(request)

    @request_mapping(path="/{id:\d+}", auth_required=False)
    async def http_get_one(self, request):
        """
        ---
        description: Get one Actor
        tags:
        - Actor
        parameters:
        - name: "id"
          in: "path"
          description: "Actor ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
            "405":
                description: invalid HTTP Met
        """
        return await super().http_get_one(request)

    @request_mapping(path="/", method="POST", auth_required=False)
    async def http_add(self, request):
        """
        ---
        description: Get one Actor
        tags:
        - Actor
        parameters:
        - in: body
          name: body
          description: Created an actor
          required: false
          schema:
            type: object
            properties:
              name:
                type: string
              type:
                type: string
              config:
                type: object
        responses:
            "204":
                description: successful operation
        """
        return await super().http_add(request)

    @request_mapping(path="/{id}", method="PUT", auth_required=False)
    async def http_update(self, request):
        """
        ---
        description: Update an actor
        tags:
        - Actor
        parameters:
        - name: "id"
          in: "path"
          description: "Actor ID"
          required: true
          type: "integer"
          format: "int64"
        - in: body
          name: body
          description: Update an actor
          required: false
          schema:
            type: object
            properties:
              name:
                type: string
              type:
                type: string
              config:
                type: object
        responses:
            "200":
                description: successful operation
        """
        return await super().http_update(request)

    @request_mapping(path="/{id}", method="DELETE", auth_required=False)
    async def http_delete_one(self, request):
        """
        ---
        description: Delete an actor
        tags:
        - Actor
        parameters:
        - name: "id"
          in: "path"
          description: "Actor ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
        """
        return await super().http_delete_one(request)

    @request_mapping(path="/{id:\d+}/on", method="POST", auth_required=auth)
    async def http_on(self, request) -> web.Response:
        """

        ---
        description: Switch actor on
        tags:
        - Actor

        parameters:
        - name: "id"
          in: "path"
          description: "Actor ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
            "405":
                description: invalid HTTP Met
        """
        id = int(request.match_info['id'])
        result = await self.cbpi.bus.fire(topic="actor/%s/switch/on" % id, id=id, power=99)
        for key, value in result.results.items():
            pass
        return web.Response(status=204)


    @request_mapping(path="/{id:\d+}/off", method="POST", auth_required=auth)
    async def http_off(self, request) -> web.Response:
        """

        ---
        description: Switch actor off
        tags:
        - Actor

        parameters:
        - name: "id"
          in: "path"
          description: "Actor ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
            "405":
                description: invalid HTTP Met
        """
        id = int(request.match_info['id'])
        await self.cbpi.bus.fire(topic="actor/%s/off" % id, id=id)
        return web.Response(status=204)

    @request_mapping(path="/{id:\d+}/toggle", method="POST", auth_required=auth)
    async def http_toggle(self, request) -> web.Response:
        """

        ---
        description: Toogle an actor on or off
        tags:
        - Actor
        parameters:
        - name: "id"
          in: "path"
          description: "Actor ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
            "405":
                description: invalid HTTP Met
        """
        id = int(request.match_info['id'])

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
        self.logger = logging.getLogger(__name__)
        self.cbpi.register(self, "/actor")
        self.types = {}
        self.actors = {}

    def info(self):

        return json.dumps(dict(name="ActorController", types=self.types), cls=ComplexEncoder)


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
        else:
            print("NOT FOUND")
            self.logger.error("Actor type '%s' not found (Available Actor Types: %s)" % (actor.type, ', '.join(self.types.keys())))



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
            self.logger.debug("ON %s" % id)
            actor = self.cache[id].instance
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

        self.logger.debug("TOGGLE %s" % id)
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

        self.logger.debug("OFF %s" % id)
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
