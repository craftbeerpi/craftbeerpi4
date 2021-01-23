import asyncio

from cbpi.api import *

@parameters([Property.Number(label="Param1", configurable=True), 
             Property.Text(label="Param2", configurable=True, default_value="HALLO"), 
             Property.Select(label="Param3", options=[1,2,4]), 
             Property.Sensor(label="Param4"), 
             Property.Actor(label="Param5")])
class CustomLogic(CBPiKettleLogic):

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
