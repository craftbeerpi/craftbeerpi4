import asyncio
import time

from cbpi.api import *


@parameters([Property.Number(label="Param1", configurable=True), 
             Property.Text(label="Param2", configurable=True, default_value="HALLO"), 
             Property.Select(label="Param3", options=[1,2,4]), 
             Property.Sensor(label="Param4"), 
             Property.Actor(label="Param5")])
class Step2(CBPiStep):

    @action(key="name2", parameters=[])
    async def action2(self, **kwargs):
        print("CALL ACTION")

    @action(key="name", parameters=[Property.Number(label="Test", configurable=True)])
    async def action(self, **kwargs):
        print("CALL ACTION")

    async def execute(self):
        count = self.props.get("count", 0)
        self.state_msg = "COUNT %s" % count

        self.props["count"] += 1
        await self.update(self.props)

        if count >= 5:
            self.next()
        
    async def reset(self): 
        self.props["count"] = 0

def setup(cbpi):
    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server

    :param cbpi: the cbpi core 
    :return: 
    '''
    cbpi.plugin.register("CustomStep2", Step2)
    
