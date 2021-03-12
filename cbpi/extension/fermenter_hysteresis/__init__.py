import asyncio
from asyncio import tasks
import logging
from cbpi.api import *

@parameters([Property.Number(label="OffsetOn", configurable=True, description="Offset below target temp when cooler should switched on"),
             Property.Number(label="OffsetOff", configurable=True, description="Offset above target temp when cooler should switched off")])
class Hysteresis(CBPiFermenterLogic):
    
    async def run(self):
        try:
            self.offset_on = float(self.props.get("OffsetOn", 0))
            self.offset_off = float(self.props.get("OffsetOff", 0))
            self.fermenter = self.get_fermenter(self.id)
            self.cooler = self.fermenter.cooler
            logging.info("Hysteresis {} {} {} {}".format(self.offset_on, self.offset_off, self.id, self.cooler))

            self.get_actor_state()


            while True:
                
                sensor_value = self.get_sensor_value(self.fermenter.sensor).get("value")
                target_temp = self.fermenter(self.id)
                if sensor_value > target_temp - self.offset_on:
                    await self.actor_on(self.cooler)
                elif sensor_value <= target_temp + self.offset_off:
                    await self.actor_off(self.cooler)
                await asyncio.sleep(1)

        except asyncio.CancelledError as e:
            pass
        except Exception as e:
            logging.error("CustomLogic Error {}".format(e))
        finally:
            self.running = False
            await self.actor_off(self.cooler)



def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("Fermentor_Hysteresis", Hysteresis)
