from abc import ABCMeta
import asyncio
from cbpi.api.config import ConfigType

__all__ = ["CBPiActor"]

import logging


logger = logging.getLogger(__file__)


class CBPiActor(metaclass=ABCMeta):

    def __init__(self, cbpi, id, props):
        self.cbpi = cbpi
        self.id = id
        self.props = props
        self.logger = logging.getLogger(__file__)
        self.data_logger = None
        self.state = False  
        self.running = False

    def init(self):
        pass

    def log_data(self, value):
        self.cbpi.log.log_data(self.id, value)
        
    def get_state(self):
        return dict(state=self.state)

    async def start(self):
        pass

    async def stop(self):
        pass

    async def on_start(self):
        pass

    async def on_stop(self):
        pass

    async def run(self):
        pass
    
    async def _run(self):

        try:
            await self.on_start()
            self.cancel_reason = await self.run()
        except asyncio.CancelledError as e:
            pass
        finally:
            await self.on_stop()



    def get_static_config_value(self,name,default):
        return self.cbpi.static_config.get(name, default)

    def get_config_value(self,name,default):
        return self.cbpi.config.get(name, default=default)

    async def set_config_value(self,name,value):
        return await self.cbpi.config.set(name,value)

    async def add_config_value(self, name, value, type: ConfigType, description, options=None):
        await self.cbpi.add(name, value, type, description, options=None)

    async def on(self, power):
        '''
        Code to switch the actor on. Power is provided as integer value  
        
        :param power: power value between 0 and 100 
        :return: None
        '''
        pass

    async def off(self):

        '''
        Code to switch the actor off
        
        :return: None 
        '''
        pass

    

