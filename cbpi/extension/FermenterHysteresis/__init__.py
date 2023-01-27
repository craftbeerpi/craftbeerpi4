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
                                await self.cbpi.fermenter.start(self.fermenter.id)
                                logging.info("Successfully switched on Ferenterlogic for Fermenter {}".format(self.fermenter.id))
                        except Exception as e:
                            logging.error("Failed to switch on FermenterLogic {} {}".format(self.fermenter.id, e))
                except:
                    pass
        except:
            pass


@parameters([Property.Number(label="HeaterOffsetOn", configurable=True, description="Offset as decimal number when the heater is switched on. Should be greater then 'HeaterOffsetOff'. For example a value of 2 switches on the heater if the current temperature is 2 degrees below the target temperature"),
             Property.Number(label="HeaterOffsetOff", configurable=True, description="Offset as decimal number when the heater is switched off. Should be smaller then 'HeaterOffsetOn'. For example a value of 1 switches off the heater if the current temperature is 1 degree below the target temperature"),
             Property.Number(label="CoolerOffsetOn", configurable=True, description="Offset as decimal number when the cooler is switched on. Should be greater then 'CoolerOffsetOff'. For example a value of 2 switches on the cooler if the current temperature is 2 degrees above the target temperature"),
             Property.Number(label="CoolerOffsetOff", configurable=True, description="Offset as decimal number when the cooler is switched off. Should be smaller then 'CoolerOffsetOn'. For example a value of 1 switches off the cooler if the current temperature is 1 degree above the target temperature"),
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
            logging.error("Fermenter Hysteresis Error {}".format(e))
        finally:
            self.running = False
            if self.heater:
                await self.actor_off(self.heater)
            if self.cooler:
                await self.actor_off(self.cooler)


@parameters([Property.Number(label="HeaterOffsetOn", configurable=True, description="Offset as decimal number when the heater is switched on. Should be greater then 'HeaterOffsetOff'. For example a value of 2 switches on the heater if the current temperature is 2 degrees below the target temperature"),
             Property.Number(label="HeaterOffsetOff", configurable=True, description="Offset as decimal number when the heater is switched off. Should be smaller then 'HeaterOffsetOn'. For example a value of 1 switches off the heater if the current temperature is 1 degree below the target temperature"),
             Property.Number(label="CoolerOffsetOn", configurable=True, description="Offset as decimal number when the cooler is switched on. Should be greater then 'CoolerOffsetOff'. For example a value of 2 switches on the cooler if the current temperature is 2 degrees below the target temperature"),
             Property.Number(label="CoolerOffsetOff", configurable=True, description="Offset as decimal number when the cooler is switched off. Should be smaller then 'CoolerOffsetOn'. For example a value of 1 switches off the cooler if the current temperature is 1 degree below the target temperature"),
             Property.Number(label="SpundingOffsetOpen", configurable=True, description="Offset above target pressure as decimal number when the valve is opened"),
             Property.Select(label="ValveRelease", options=[1,2,3,4,5],description="Valve Release time in seconds"),
             Property.Select(label="Pause", options=[1,2,3,4,5],description="Pause time in seconds between valve release"),
             Property.Select(label="AutoStart", options=["Yes","No"],description="Autostart Fermenter on cbpi start"),
             Property.Sensor(label="sensor2",description="Optional Sensor for LCDisplay(e.g. iSpindle)")])

class FermenterSpundingHysteresis(CBPiFermenterLogic):
    # subroutine that controls pressure
    async def pressure_control(self):
        self.spunding_offset=float(self.props.get("SpundingOffsetOpen",0))
        self.valverelease=int(self.props.get("ValveRelease",1))
        self.pause=int(self.props.get("Pause",2))
        if self.valve and self.fermenter.pressure_sensor:
            #valve = self.cbpi.actor.find_by_id(self.valve)

            await self.actor_off(self.valve)
            #logging.info("Closing Spunding Valve")

            while self.running:
                target_pressure=float(self.fermenter.target_pressure)
                current_pressure = float(self.get_sensor_value(self.fermenter.pressure_sensor).get("value"))
                #logging.info(f'Target: {target_pressure} | Current: {current_pressure}')
                if current_pressure >= (target_pressure + self.spunding_offset) and target_pressure !=0:
                    while current_pressure >= target_pressure:
                        await self.actor_on(self.valve) 
                        await asyncio.sleep(self.valverelease)
                        await self.actor_off(self.valve) 
                        await asyncio.sleep(self.pause)
                        current_pressure = float(self.get_sensor_value(self.fermenter.pressure_sensor).get("value"))
                        #logging.info("Value higher than target: Spunding loop is running")

                await asyncio.sleep(1)
        else:
            logging.info("No valve or pressure sensor defined")

    async def temperature_control(self):
            self.heater_offset_min = float(self.props.get("HeaterOffsetOn", 0))
            self.heater_offset_max = float(self.props.get("HeaterOffsetOff", 0))
            self.cooler_offset_min = float(self.props.get("CoolerOffsetOn", 0))
            self.cooler_offset_max = float(self.props.get("CoolerOffsetOff", 0))
        
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
    
    async def run(self):
        try:
            self.fermenter = self.get_fermenter(self.id)
            self.heater = self.fermenter.heater
            self.cooler = self.fermenter.cooler
            self.valve = self.fermenter.valve

            pressure_controller = asyncio.create_task(self.pressure_control())
            temperature_controller = asyncio.create_task(self.temperature_control())

            await pressure_controller
            await temperature_controller

        except asyncio.CancelledError as e:
            pass
        except Exception as e:
            logging.error("Fermenter Spunding Hysteresis Error {}".format(e))
        finally:
            self.running = False
            if self.heater:
                await self.actor_off(self.heater)
            if self.cooler:
                await self.actor_off(self.cooler)
            if self.valve:
                await self.actor_off(self.valve)

def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''
    cbpi.plugin.register("Fermenter Spunding Hysteresis", FermenterSpundingHysteresis)
    cbpi.plugin.register("Fermenter Hysteresis", FermenterHysteresis)
    cbpi.plugin.register("Fermenter Autostart", FermenterAutostart)

