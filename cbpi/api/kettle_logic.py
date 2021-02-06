from cbpi.api.extension import CBPiExtension
from abc import ABCMeta
import logging
import asyncio



class CBPiKettleLogic(metaclass=ABCMeta):

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

    async def run(self):
        self.state = True
        while self.running:
            await asyncio.sleep(1)
        self.state = False
        
    def get_state(self):
        return dict(running=self.running)

    async def start(self):
        self.running = True

    async def stop(self):
        self.running = False

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
