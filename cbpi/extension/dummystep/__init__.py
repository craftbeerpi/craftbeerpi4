import asyncio
import time

from cbpi.api import *


class CustomStepCBPi(CBPiSimpleStep):

    name1 = Property.Number(label="Test", configurable=True)
    timer_end = Property.Number(label="Test", default_value=None)
    temp = Property.Number(label="Temperature", default_value=50, configurable=True)



    i = 0
    
    @action(key="name", parameters=None)
    def test(self, **kwargs):
        self.name="WOOHOO"

    def get_status(self):
        return "Status: %s Temp" % self.temp

    async def run_cycle(self):

        self.next()

        '''
        print("RUN", self.name1, self.managed_fields, self.timer_end)
        self.i = self.i + 1

        if self.timer_end is None:
            self.timer_end = time.time() + 10

        if self.i == 10:
            self.next()
        '''

        #self.cbpi.notify(key="step", message="HELLO FROM STEP")

@parameters([Property.Number(label="Test", configurable=True), Property.Text(label="Test", configurable=True, default_value="HALLO")])
class Step2(CBPiStep):

    i = 0

    @action(key="name", parameters=[Property.Number(label="Test", configurable=True)])
    async def action(self, **kwargs):
        print("HALLO")

    async def execute(self):

        print(self.props)
        self.i += 1
        print(self.i)
        self.state_msg = "COUNT %s" % self.i
        await self.update(self.props)
        print("JETZT GEHTS LO")
        #raise Exception("RROR")


def setup(cbpi):
    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server

    :param cbpi: the cbpi core 
    :return: 
    '''
    cbpi.plugin.register("CustomStep2", Step2)
    cbpi.plugin.register("CustomStepCBPi", CustomStepCBPi)
