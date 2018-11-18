import asyncio
import logging

from core.api import CBPiActor, Property, action, background_task
from core.api.sensor import CBPiSensor


class CustomSensor(CBPiSensor):

    name = Property.Number(label="Test")
    name1 = Property.Text(label="Test")
    interval = Property.Number(label="interval")
    name2 = Property.Kettle(label="Test")

    value = 0

    @action(key="name", parameters={})
    def myAction(self):
        pass

    def state(self):
        super().state()

    def stop(self):
        pass

    async def run(self, cbpi):
        self.value = 0
        while True:
            await asyncio.sleep(self.interval)

            self.value = self.value + 1
            print("SENSOR IS RUNNING")




def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("CustomSensor", CustomSensor)
