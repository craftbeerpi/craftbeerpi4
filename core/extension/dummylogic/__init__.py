import asyncio

from core.api import Property
from core.api.kettle_logic import CBPiKettleLogic


class CustomLogic(CBPiKettleLogic):

    name = Property.Number(label="Test")

    running = True

    async def run(self):

        while self.running:

            print("RUN")
            await asyncio.sleep(1)

def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("CustomKettleLogic", CustomLogic)
