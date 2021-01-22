import asyncio

from cbpi.api import *

class CustomLogic(CBPiKettleLogic2):

    pass

    @action(key="test", parameters=[])
    async def action1(self, **kwargs):
        print("ACTION")
   



def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("CustomKettleLogic", CustomLogic)
