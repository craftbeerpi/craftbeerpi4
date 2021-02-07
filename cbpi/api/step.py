import json
import time
import asyncio
import logging
from abc import abstractmethod, ABCMeta
import logging
from cbpi.api.config import ConfigType

class CBPiStep(metaclass=ABCMeta):
    def __init__(self, cbpi, id, name, props) :
        self.cbpi = cbpi
        self.props = {**props}
        self.id = id
        self.name = name
        self.status = 0
        self.running = False
        self.stop_reason = None
        self.pause = False
        self.task = None
        self._exception_count = 0
        self._max_exceptions = 2
        self.state_msg = "No state"

    def get_state(self):
        return self.state_msg

    def stop(self):
        self.stop_reason = "STOP"
        self.running = False
        
    def start(self):
        self.running = True
        self.stop_reason = None
    
    def next(self):
        self.stop_reason = "NEXT"
        self.running = False

    async def reset(self): 
        pass

    async def update(self, props):
        await self.cbpi.step.update_props(self.id, props)

    async def run(self): 
        while self.running:
            try:
                await self.execute()
            except Exception as e:
                self._exception_count += 1
                logging.error("Step has thrown exception")
                if self._exception_count >= self._max_exceptions:
                    self.stop_reason = "MAX_EXCEPTIONS"
                    return (self.id, self.stop_reason)
            await asyncio.sleep(1)
        
        return (self.id, self.stop_reason)
        

    @abstractmethod
    async def execute(self):
        pass

    def get_static_config_value(self,name,default):
        return self.cbpi.static_config.get(name, default)

    def get_config_value(self,name,default):
        return self.cbpi.config.get(name, default=default)

    async def set_config_value(self,name,value):
        return await self.cbpi.config.set(name,value)

    async def add_config_value(self, name, value, type: ConfigType, description, options=None):
        await self.cbpi.add(name, value, type, description, options=None)

    def get_kettle(self,id):
        return self.cbpi.kettle.find_by_id(id)

    async def set_target_temp(self,id, temp):
        await self.cbpi.kettle.set_target_temp(id, temp)

    def get_sensor(self,id):
        return self.cbpi.sensor.find_by_id(id)

    def get_actor(self,id):
        return self.cbpi.actor.find_by_id(id)

    def get_actor_state(self,id):
        try:
            actor = self.cbpi.actor.find_by_id(id)
            return actor.get("instance").get_state()
        except:
            logging.error("Faild to read actor state in step - actor {}".format(id))
            return None

    async def actor_on(self,id):
        
        try:
            await self.cbpi.actor.on(id)
        except:
            pass

    async def actor_off(self,id):
        try:
            await self.cbpi.actor.off(id)
        except:
            pass