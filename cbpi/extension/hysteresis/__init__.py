import asyncio
from asyncio import tasks
import logging
from cbpi.api import *

@parameters([Property.Number(label="OffsetOn", configurable=True, description="Offset below target temp when heater should switched on"),
             Property.Number(label="OffsetOff", configurable=True, description="Offset below target temp when heater should switched off")])
class Hysteresis(CBPiKettleLogic):
    
    async def run(self):
        try:
            self.offset_on = float(self.props.get("OffsetOn", 0))
            self.offset_off = float(self.props.get("OffsetOff", 0))
            self.kettle = self.get_kettle(self.id)
            self.heater = self.kettle.heater
            heater = self.cbpi.actor.find_by_id(self.heater)
            logging.info("Hysteresis {} {} {} {}".format(self.offset_on, self.offset_off, self.id, self.heater))

            # self.get_actor_state()
	    

            while self.running == True:
                
                sensor_value = self.get_sensor_value(self.kettle.sensor).get("value")
                target_temp = self.get_kettle_target_temp(self.id)
                try:
                    heater_state=heater.instance.state
                except:
                    heater_state = False
                if sensor_value < target_temp - self.offset_on:
                    if self.heater and (heater_state == False):
                        await self.actor_on(self.heater)
                elif sensor_value >= target_temp - self.offset_off:
                    if self.heater and (heater_state == True):
                        await self.actor_off(self.heater)
                await asyncio.sleep(1)

        except asyncio.CancelledError as e:
            pass
        except Exception as e:
            logging.error("CustomLogic Error {}".format(e))
        finally:
            self.running = False
            await self.actor_off(self.heater)



def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("Hysteresis", Hysteresis)
