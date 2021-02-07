import asyncio
import time
import random
from cbpi.api import *


@parameters([Property.Number(label="Timer", configurable=True), 
             Property.Number(label="Temp", configurable=True),
             Property.Kettle(label="Kettle")])
class MashStep(CBPiStep):


    async def execute(self):
        try:
            kid = self.props.get("Kettle", None)
            kettle = self.get_kettle(kid)
            actor = self.get_actor(kettle.get("heater"))
            print(self.get_actor_state(kettle.get("heater")))
            await self.cbpi.kettle.set_target_temp(kid, random.randint(0,50))
            if self.v is True:
                await self.actor_on(kettle.get("heater"))
            else:
                await self.actor_off(kettle.get("heater"))
            self.v = not self.v
        except:
            pass
        
       
def setup(cbpi):
    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server

    :param cbpi: the cbpi core 
    :return: 
    '''
    cbpi.plugin.register("MashStep", MashStep)
    
