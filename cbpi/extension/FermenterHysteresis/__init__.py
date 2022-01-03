import asyncio
from asyncio import tasks
import logging
from cbpi.api import *
import aiohttp
from aiohttp import web
from cbpi.controller.fermentation_controller import FermentationController
from cbpi.api.dataclasses import Fermenter, Props, Step
from cbpi.api.base import CBPiBase
from cbpi.api.config import ConfigType
import json
import webbrowser

class FermenterAutostart(CBPiExtension):

    def __init__(self,cbpi):
        self.cbpi = cbpi
        self._task = asyncio.create_task(self.run())
        self.controller : FermentationController = cbpi.fermenter

    async def run(self):
        logging.info("Starting Fermenter Autorun")
        #get all kettles
        try:
            self.fermenter = self.controller.get_state()
            for id in self.fermenter['data']:
                try:
                    self.autostart=(id['props']['AutoStart'])
                    if self.autostart == "Yes":
                        fermenter_id=(id['id'])
                        logging.info("Enabling Autostart for Fermenter {}".format(fermenter_id))
                        self.fermenter=self.cbpi.fermenter._find_by_id(fermenter_id)
                        try:
                            if (self.fermenter.instance is None or self.fermenter.instance.state == False):
                                await self.cbpi.fermenter.toggle(self.fermenter.id)
                                logging.info("Successfully switched on Ferenterlogic for Fermenter {}".format(self.fermenter.id))
                        except Exception as e:
                            logging.error("Failed to switch on FermenterLogic {} {}".format(self.fermenter.id, e))
                except:
                    pass
        except:
            pass


@parameters([Property.Number(label="HeaterOffsetOn", configurable=True, description="Offset as decimal number when the heater is switched on. Should be greater then 'HeaterOffsetOff'. For example a value of 2 switches on the heater if the current temperature is 2 degrees below the target temperature"),
             Property.Number(label="HeaterOffsetOff", configurable=True, description="Offset as decimal number when the heater is switched off. Should be smaller then 'HeaterOffsetOn'. For example a value of 1 switches off the heater if the current temperature is 1 degree below the target temperature"),
             Property.Number(label="CoolerOffsetOn", configurable=True, description="Offset as decimal number when the cooler is switched on. Should be greater then 'CoolerOffsetOff'. For example a value of 2 switches on the cooler if the current temperature is 2 degrees below the target temperature"),
             Property.Number(label="CoolerOffsetOff", configurable=True, description="Offset as decimal number when the cooler is switched off. Should be smaller then 'CoolerOffsetOn'. For example a value of 1 switches off the cooler if the current temperature is 1 degree below the target temperature"),
             Property.Select(label="AutoStart", options=["Yes","No"],description="Autostart Fermenter on cbpi start"),
             Property.Sensor(label="sensor2",description="Optional Sensor for LCDisplay(e.g. iSpindle)")])

class FermenterHysteresis(CBPiFermenterLogic):
    
    async def run(self):
        try:
            self.heater_offset_min = float(self.props.get("HeaterOffsetOn", 0))
            self.heater_offset_max = float(self.props.get("HeaterOffsetOff", 0))
            self.cooler_offset_min = float(self.props.get("CoolerOffsetOn", 0))
            self.cooler_offset_max = float(self.props.get("CoolerOffsetOff", 0))
        
            self.fermenter = self.get_fermenter(self.id)
            self.heater = self.fermenter.heater
            self.cooler = self.fermenter.cooler

            heater = self.cbpi.actor.find_by_id(self.heater)
            cooler = self.cbpi.actor.find_by_id(self.cooler)

            while self.running == True:
                
                sensor_value = float(self.get_sensor_value(self.fermenter.sensor).get("value"))
                target_temp = float(self.get_fermenter_target_temp(self.id))

                try:
                    heater_state = heater.instance.state
                except:
                    heater_state= False
                try:
                    cooler_state = cooler.instance.state
                except:
                    cooler_state= False

                if sensor_value + self.heater_offset_min <= target_temp:
                    if self.heater and (heater_state == False):
                        await self.actor_on(self.heater)
                    
                if sensor_value + self.heater_offset_max >= target_temp:
                    if self.heater and (heater_state == True):
                        await self.actor_off(self.heater)

                if sensor_value >=  self.cooler_offset_min + target_temp:
                    if self.cooler and (cooler_state == False):
                        await self.actor_on(self.cooler)
                    
                if sensor_value <= self.cooler_offset_max + target_temp:
                    if self.cooler and (cooler_state == True):
                        await self.actor_off(self.cooler)

                await asyncio.sleep(1)

        except asyncio.CancelledError as e:
            pass
        except Exception as e:
            logging.error("CustomLogic Error {}".format(e))
        finally:
            self.running = False
            if self.heater:
                await self.actor_off(self.heater)
            if self.cooler:
                await self.actor_off(self.cooler)



def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("Fermenter Hysteresis", FermenterHysteresis)
    cbpi.plugin.register("Fermenter Autostart", FermenterAutostart)

