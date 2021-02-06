import asyncio

from cbpi.api import *

@parameters([])
class CustomLogic(CBPiKettleLogic):

    async def run(self):
        self.state = True
        while self.running:
            await asyncio.sleep(1)
        self.state = False



def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("CustomKettleLogic", CustomLogic)
