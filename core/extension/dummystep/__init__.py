import asyncio

from cbpi_api import *


class CustomStepCBPi(CBPiSimpleStep):

    name = Property.Number(label="Test")

    i = 0
    
    @action(key="name", parameters=None)
    def test(self, **kwargs):
        self.name="WOOHOO"

    async def run_cycle(self):


        #await asyncio.sleep(1)
        self.i = self.i + 1
        self.name="HALLO WELT"
        if self.i == 20:
            self.next()
        self.cbpi.notify(key="step", message="HELLO FROM STEP")



def setup(cbpi):
    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server

    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("CustomStepCBPi", CustomStepCBPi)
