import logging
from asyncio import Future

from cbpi_api import *
from voluptuous import Schema

from core.controller.crud_controller import CRUDController
from core.database.model import ActorModel


class ActorController(CRUDController):
    '''
    The main actor controller
    '''
    model = ActorModel

    def __init__(self, cbpi):
        super(ActorController, self).__init__(cbpi)
        self.cbpi = cbpi
        self.state = False;
        self.logger = logging.getLogger(__name__)
        self.cbpi.register(self)
        self.types = {}
        self.actors = {}

    async def init(self):
        """
        This method initializes all actors during startup. It creates actor instances
        
        :return: 
        """
        await super(ActorController, self).init()
        for id, value in self.cache.items():
            await self._init_actor(value)

    def get_state(self):
        return dict(items=self.cache,types=self.types)

    async def _init_actor(self, actor):

        try:
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
        except Exception as e:
            self.logger.error("Failed to init actor %s - Reason %s" % (actor.id, str(e)))

    async def _stop_actor(self, actor):
        actor.instance.stop()
        await self.cbpi.bus.fire(topic="actor/%s/stopped" % actor.id, id=actor.id)

    @on_event(topic="actor/+/switch/on")
    async def on(self, actor_id, future: Future, power=100, **kwargs) -> None:
        """
        Method to switch an actor on.
        Supporting Event Topic "actor/+/on"
        
        :param actor_id: the actor id
        :param future
        :param power: as integer value between 1 and 100
        :param kwargs: 
        :return: 
        """

        actor_id = int(actor_id)
        if actor_id in self.cache:
            self.logger.debug("ON %s" % actor_id)
            actor = self.cache[actor_id].instance
            await self.cbpi.bus.fire("actor/%s/on/ok" % actor_id)
            actor.on(power)

        future.set_result("OK")

    @on_event(topic="actor/+/toggle")
    async def toggle(self, actor_id, power=100, **kwargs) -> None:
        """
        Method to toggle an actor on or off
        Supporting Event Topic "actor/+/toggle"

        :param actor_id: the actor actor_id
        :param power: the power as integer between 0 and 100
        :return:
        """

        self.logger.debug("TOGGLE %s" % actor_id)
        actor_id = int(actor_id)
        if actor_id in self.cache:
            actor = self.cache[actor_id].instance
            if actor.state is True:
                actor.off()
            else:
                actor.on()


    @on_event(topic="actor/+/off")
    async def off(self, actor_id, **kwargs) -> None:
        """
        Method to switch and actor off
        Supporting Event Topic "actor/+/off"
        
        :param actor_id: the actor actor_id
        :param kwargs: 
        """
        self.logger.debug("OFF %s" % actor_id)
        actor_id = int(actor_id)

        if actor_id in self.cache:
            actor = self.cache[actor_id].instance
            actor.off()

    @on_event(topic="actor/+/action")
    async def call_action(self, actor_id, data, **kwargs) -> None:

        schema = Schema({"name":str, "parameter":dict})
        schema(data)
        name = data.get("name")
        parameter = data.get("parameter")
        actor = self.cache[actor_id].instance.__getattribute__(name)(**parameter)

    async def _post_add_callback(self, m):
        '''
    
        :param m: 
        :return: 
        '''
        await self._init_actor(m)
        pass

    async def _pre_delete_callback(self, actor_id):
        #if int(actor_id) not in self.cache:
        #    return
        if self.cache[int(actor_id)].instance is not None:
            await self._stop_actor(self.cache[int(actor_id)])

    async def _pre_update_callback(self, actor):
        if actor.instance is not None:
            await self._stop_actor(actor)

    async def _post_update_callback(self, actor):
        self._init_actor(actor)
