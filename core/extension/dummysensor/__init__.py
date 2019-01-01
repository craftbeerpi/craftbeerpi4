import asyncio
import logging
import random

from cbpi_api import *

class CustomSensor(CBPiSensor):

    # Custom Properties which will can be configured by the user

    p1 = Property.Number(label="Test")
    p2 = Property.Text(label="Test")
    interval = Property.Number(label="interval")

    # Internal runtime variable
    value = 0

    @action(key="name", parameters={})
    def myAction(self):
        '''
        Custom Action Exampel
        :return: None
        '''
        pass

    def init(self):
        super().init()


    def state(self):
        super().state()

    def stop(self):
        pass

    async def run(self, cbpi):
        self.value = 0
        while True:
            await asyncio.sleep(self.interval)
            self.log_data(10)
            self.value = self.value + 1
            await cbpi.bus.fire("sensor/%s" % self.id, value=self.value)





def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("CustomSensor", CustomSensor)
