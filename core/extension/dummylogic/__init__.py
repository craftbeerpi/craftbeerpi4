import asyncio

from core.api import Property
from core.api.kettle_logic import CBPiKettleLogic


class CustomLogic(CBPiKettleLogic):

    test = Property.Number(label="Test")


    running = True

    async def run(self):

        while self.running:

            print("RUN", self.test)
            value = await self.cbpi.sensor.get_value(1)
            print(value)
            if value >= 10:
                break
            await asyncio.sleep(1)

        print("STOP LOGIC")

def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("CustomKettleLogic", CustomLogic)
