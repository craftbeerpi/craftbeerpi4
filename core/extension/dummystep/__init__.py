import asyncio

from core.api import Property, action
from core.api.step import Step


class CustomStep(Step):

    name = Property.Number(label="Test")
    _interval = 1
    
    @action(key="name", parameters=None)
    def test(self, **kwargs):
        self.name="WOOHOO"

    async def run(self):

        #await asyncio.sleep(1)

        print("RUN STEP", self.id, self.name, self.__dict__)


def setup(cbpi):
    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server

    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("CustomStep", CustomStep)
