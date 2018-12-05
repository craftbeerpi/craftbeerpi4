import asyncio

from core.api import Property
from core.api.step import Step


class CustomStep(Step):

    name = Property.Number(label="Test")


    async def run(self):
        self.name = "HELLO WORLD"
        #await asyncio.sleep(1)
        raise Exception("OH O")
        print("RUN STEP", self.id, self.name, self.__dict__)


def setup(cbpi):
    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server

    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("CustomStep", CustomStep)
