from cbpi.api.extension import CBPiExtension
from abc import ABCMeta
import logging
import asyncio

class CBPiKettleLogic(CBPiExtension):

    '''
    Base Class for a Kettle logic. 
    '''

    def init(self):
        '''
        Code which will be executed when the logic is initialised. Needs to be overwritten by the implementing logic
        
        :return: None
        '''
        pass

    def stop(self):
        '''
        Code which will be executed when the logic is stopped. Needs to be overwritten by the implementing logic
        
        
        :return: None
        '''
        pass

    def run(self):
        '''
        This method is running as background process when logic is started.
        Typically a while loop responsible that the method keeps running 
        
            while self.running:
                await asyncio.sleep(1)
        
        :return: None
        '''

        pass


class CBPiKettleLogic2(metaclass=ABCMeta):

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
        while self.running:
            print("RUNNING KETTLE")
            await asyncio.sleep(1)
        
    def get_state(self):
        print("########STATE", self.state)
        return dict(state=self.state)

    async def start(self):
        print("")
        print("")
        print("")
        print("##################START UP KETTLE")
        print("")
        print("")
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
