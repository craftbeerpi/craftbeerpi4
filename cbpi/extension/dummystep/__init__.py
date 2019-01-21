import asyncio

from cbpi.api import *


class CustomStepCBPi(CBPiSimpleStep):

    name = Property.Number(label="Test")

    i = 0
    
    @action(key="name", parameters=None)
    def test(self, **kwargs):
        self.name="WOOHOO"

    async def run_cycle(self):
        print("RUN", self.name)
        self.i = self.i + 1
        await asyncio.sleep(5)
        print("WAIT")
        self.next()
        #if self.i == 5:
        #    print("NEXT")


        #self.cbpi.notify(key="step", message="HELLO FROM STEP")



def setup(cbpi):
    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server

    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("CustomStepCBPi", CustomStepCBPi)
