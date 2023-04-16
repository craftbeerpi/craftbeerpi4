import os, threading, time, shutil
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
import json
from cbpi.api import *
from cbpi.api.config import ConfigType
from cbpi.api.base import CBPiBase
from cbpi import __version__

logger = logging.getLogger(__name__)

class ConfigUpdate(CBPiExtension):

    def __init__(self,cbpi):
        self.cbpi = cbpi
        self._task = asyncio.create_task(self.run())


    async def run(self):
        logging.info("Check Config for required changes")

        # check is default steps are config parameters

        TEMP_UNIT = self.cbpi.config.get("TEMP_UNIT", "C")
        default_boil_temp = 99 if TEMP_UNIT == "C" else 212
        default_cool_temp = 20 if TEMP_UNIT == "C" else 68
        boil_temp = self.cbpi.config.get("steps_boil_temp", None)
        cooldown_sensor = self.cbpi.config.get("steps_cooldown_sensor", None)
        cooldown_actor = self.cbpi.config.get("steps_cooldown_actor", None)
        cooldown_temp = self.cbpi.config.get("steps_cooldown_temp", None)
        mashin_step = self.cbpi.config.get("steps_mashin", None)
        mash_step = self.cbpi.config.get("steps_mash", None)
        mashout_step = self.cbpi.config.get("steps_mashout", None)
        boil_step = self.cbpi.config.get("steps_boil", None)
        cooldown_step = self.cbpi.config.get("steps_cooldown", None)
        max_dashboard_number = self.cbpi.config.get("max_dashboard_number", None)
        current_dashboard_number = self.cbpi.config.get("current_dashboard_number", None)
        logfiles = self.cbpi.config.get("CSVLOGFILES", None)
        influxdb = self.cbpi.config.get("INFLUXDB", None)
        influxdbaddr = self.cbpi.config.get("INFLUXDBADDR", None)
        influxdbname = self.cbpi.config.get("INFLUXDBNAME", None)
        influxdbuser = self.cbpi.config.get("INFLUXDBUSER", None)
        influxdbpwd = self.cbpi.config.get("INFLUXDBPWD", None)
        influxdbcloud = self.cbpi.config.get("INFLUXDBCLOUD", None)
        influxdbmeasurement = self.cbpi.config.get("INFLUXDBMEASUREMENT", None)
        mqttupdate = self.cbpi.config.get("MQTTUpdate", None)
        PRESSURE_UNIT = self.cbpi.config.get("PRESSURE_UNIT", None)
        SENSOR_LOG_BACKUP_COUNT = self.cbpi.config.get("SENSOR_LOG_BACKUP_COUNT", None)
        SENSOR_LOG_MAX_BYTES = self.cbpi.config.get("SENSOR_LOG_MAX_BYTES", None)
        slow_pipe_animation = self.cbpi.config.get("slow_pipe_animation", None)
        NOTIFY_ON_ERROR = self.cbpi.config.get("NOTIFY_ON_ERROR", None)
        PLAY_BUZZER = self.cbpi.config.get("PLAY_BUZZER", None)
        BoilAutoTimer = self.cbpi.config.get("BoilAutoTimer", None)
        MASH_TUN = self.cbpi.config.get("MASH_TUN", None)
        AutoMode = self.cbpi.config.get("AutoMode", None)
        AddMashIn = self.cbpi.config.get("AddMashInStep", None)
        bfuserid = self.cbpi.config.get("brewfather_user_id", None)
        bfapikey = self.cbpi.config.get("brewfather_api_key", None)
        RecipeCreationPath = self.cbpi.config.get("RECIPE_CREATION_PATH", None)
        BoilKettle = self.cbpi.config.get("BoilKettle", None)
        CONFIG_STATUS = self.cbpi.config.get("CONFIG_STATUS", None)
        self.version=__version__


        if boil_temp is None:
            logger.info("INIT Boil Temp Setting")
            try:
                await self.cbpi.config.add("steps_boil_temp", default_boil_temp, type=ConfigType.NUMBER, description="Default Boil Temperature for Recipe Creation", source="steps")
            except:
                logger.warning('Unable to update database')
        else: 
            if CONFIG_STATUS is None or CONFIG_STATUS != self.version:
                await self.cbpi.config.add("steps_boil_temp", boil_temp, type=ConfigType.NUMBER, description="Default Boil Temperature for Recipe Creation", source="steps")

        if cooldown_sensor is None:
            logger.info("INIT Cooldown Sensor Setting")
            try:
                await self.cbpi.config.add("steps_cooldown_sensor", "", type=ConfigType.SENSOR, description="Alternative Sensor to monitor temperature durring cooldown (if not selected, Kettle Sensor will be used)", source="steps")
            except:
                logger.warning('Unable to update database')
        else: 
            if CONFIG_STATUS is None or CONFIG_STATUS != self.version:
                await self.cbpi.config.add("steps_cooldown_sensor", cooldown_sensor, type=ConfigType.SENSOR, description="Alternative Sensor to monitor temperature durring cooldown (if not selected, Kettle Sensor will be used)", source="steps")

        if cooldown_actor is None:
            logger.info("INIT Cooldown Actor Setting")
            try:
                await self.cbpi.config.add("steps_cooldown_actor", "", type=ConfigType.ACTOR, description="Actor to trigger cooldown water on and off (default: None)", source="steps")
            except:
                logger.warning('Unable to update database')
        else: 
            if CONFIG_STATUS is None or CONFIG_STATUS != self.version:
                await self.cbpi.config.add("steps_cooldown_actor", cooldown_actor, type=ConfigType.ACTOR, description="Actor to trigger cooldown water on and off (default: None)", source="steps")

        if cooldown_temp is None:
            logger.info("INIT Cooldown Temp Setting")
            try:
                await self.cbpi.config.add("steps_cooldown_temp", default_cool_temp, type=ConfigType.NUMBER, description="Cooldown temp will send notification when this temeprature is reached", source="steps")
            except:
                logger.warning('Unable to update database')
        else: 
            if CONFIG_STATUS is None or CONFIG_STATUS != self.version:    
                await self.cbpi.config.add("steps_cooldown_temp", cooldown_temp, type=ConfigType.NUMBER, description="Cooldown temp will send notification when this temeprature is reached", source="steps")                            

        if cooldown_step is None:
            logger.info("INIT Cooldown Step Type")
            try:
                await self.cbpi.config.add("steps_cooldown", "", type=ConfigType.STEP, description="Cooldown step type", source="steps")
            except:
                logger.warning('Unable to update database')
        else: 
            if CONFIG_STATUS is None or CONFIG_STATUS != self.version:
                await self.cbpi.config.add("steps_cooldown", cooldown_step, type=ConfigType.STEP, description="Cooldown step type", source="steps")                

        if mashin_step is None:
            logger.info("INIT MashIn Step Type")
            try:
                await self.cbpi.config.add("steps_mashin", "", type=ConfigType.STEP, description="MashIn step type", source="steps")
            except:
                logger.warning('Unable to update database')
        else: 
            if CONFIG_STATUS is None or CONFIG_STATUS != self.version:                
                await self.cbpi.config.add("steps_mashin", mashin_step, type=ConfigType.STEP, description="MashIn step type", source="steps")

        if mash_step is None:
            logger.info("INIT Mash Step Type")
            try:
                await self.cbpi.config.add("steps_mash", "", type=ConfigType.STEP, description="Mash step type", source="steps")
            except:
                logger.warning('Unable to update database')
        else: 
            if CONFIG_STATUS is None or CONFIG_STATUS != self.version:                
                await self.cbpi.config.add("steps_mash", mash_step, type=ConfigType.STEP, description="Mash step type", source="steps")                

        if mashout_step is None:
            logger.info("INIT MashOut Step Type")
            try:
                await self.cbpi.config.add("steps_mashout", "", type=ConfigType.STEP, description="MashOut step type", source="steps")
            except:
                logger.warning('Unable to update database')
        else: 
            if CONFIG_STATUS is None or CONFIG_STATUS != self.version:                
                await self.cbpi.config.add("steps_mashout", mashout_step, type=ConfigType.STEP, description="MashOut step type", source="steps")                

        if boil_step is None:
            logger.info("INIT Boil Step Type")
            try:
                await self.cbpi.config.add("steps_boil", "", type=ConfigType.STEP, description="Boil step type", source="steps")
            except:
                logger.warning('Unable to update database')
        else: 
            if CONFIG_STATUS is None or CONFIG_STATUS != self.version:             
                await self.cbpi.config.add("steps_boil", boil_step, type=ConfigType.STEP, description="Boil step type", source="steps")                   

        if max_dashboard_number is None:
            logger.info("INIT Max Dashboard Numbers for multiple dashboards")
            try:
                await self.cbpi.config.add("max_dashboard_number", 4, type=ConfigType.SELECT, description="Max Number of Dashboards",
                                                                                                source="craftbeerpi",
                                                                                               options= [{"label": "1", "value": 1},
                                                                                                {"label": "2", "value": 2},
                                                                                                {"label": "3", "value": 3},
                                                                                                {"label": "4", "value": 4},
                                                                                                {"label": "5", "value": 5},
                                                                                                {"label": "6", "value": 6},
                                                                                                {"label": "7", "value": 7},
                                                                                                {"label": "8", "value": 8},
                                                                                                {"label": "9", "value": 9},
                                                                                                {"label": "10", "value": 10}])
                                                                                                
            except:
                logger.warning('Unable to update database')

        if current_dashboard_number is None:
            logger.info("INIT Current Dashboard Number")
            try:
                await self.cbpi.config.add("current_dashboard_number", 1, type=ConfigType.NUMBER, description="Number of current Dashboard",source="hidden")
            except:
                logger.warning('Unable to update database')
        else: 
            if CONFIG_STATUS is None or CONFIG_STATUS != self.version:
                await self.cbpi.config.add("current_dashboard_number", current_dashboard_number, type=ConfigType.NUMBER, description="Number of current Dashboard",source="hidden")

       ## Check if AtuoMode for Steps is in config

        if AutoMode is None:
            logger.info("INIT AutoMode")
            try:
                await self.cbpi.config.add("AutoMode", "Yes", type=ConfigType.SELECT, description="Use AutoMode in steps", 
                                                                                        source="steps",
                                                                                        options=[{"label": "Yes", "value": "Yes"},
                                                                                                {"label": "No", "value": "No"}])
                                                                                                
            except:
                logger.warning('Unable to update config')
        else: 
            if CONFIG_STATUS is None or CONFIG_STATUS != self.version:                
                await self.cbpi.config.add("AutoMode", AutoMode, type=ConfigType.SELECT, description="Use AutoMode in steps", 
                                                                                            source="steps",
                                                                                            options=[{"label": "Yes", "value": "Yes"},
                                                                                                {"label": "No", "value": "No"}])
                                                                                                

        ## Check if AddMashInStep for Steps is in config

        if AddMashIn is None:
            logger.info("INIT AddMashInStep")
            try:
                await self.cbpi.config.add("AddMashInStep", "Yes", type=ConfigType.SELECT, description= "Add MashIn Step automatically if not defined in recipe", 
                                                                                                source="steps",
                                                                                               options = [{"label": "Yes", "value": "Yes"},
                                                                                                {"label": "No", "value": "No"}])
                                                                                                
            except:
                logger.warning('Unable to update config')
        else: 
            if CONFIG_STATUS is None or CONFIG_STATUS != self.version:      
                await self.cbpi.config.add("AddMashInStep", AddMashIn, type=ConfigType.SELECT, description="Add MashIn Step automatically if not defined in recipe", 
                                                                                                source="steps",
                                                                                               options= [{"label": "Yes", "value": "Yes"},
                                                                                                {"label": "No", "value": "No"}])
                                                                                                

        ## Check if Brewfather UserID is in config

        if bfuserid is None:
            logger.info("INIT Brewfather User ID")
            try:
                await self.cbpi.config.add("brewfather_user_id", "", type=ConfigType.STRING, description="Brewfather User ID", source="craftbeerpi")
            except:
                logger.warning('Unable to update config')

        ## Check if Brewfather API Key is in config
        
        if bfapikey is None:
            logger.info("INIT Brewfather API Key")
            try:
                await self.cbpi.config.add("brewfather_api_key", "", type=ConfigType.STRING, description="Brewfather API Key", source="craftbeerpi")
            except:
                logger.warning('Unable to update config')

        ## Check if Brewfather API Key is in config
        
        if RecipeCreationPath is None:
            logger.info("INIT Recipe Creation Path")
            try:
                await self.cbpi.config.add("RECIPE_CREATION_PATH", "upload", type=ConfigType.STRING, description="API path to creation plugin. Default: upload . CHANGE ONLY IF USING A RECIPE CREATION PLUGIN", source="craftbeerpi")
            except:
                logger.warning('Unable to update config')

        ## Check if  Kettle for Boil, Whirlpool and Cooldown is in config
        
        if BoilKettle is None:
            logger.info("INIT BoilKettle")
            try:
                await self.cbpi.config.add("BoilKettle", "", type=ConfigType.KETTLE, description="Define Kettle that is used for Boil, Whirlpool and Cooldown. If not selected, MASH_TUN will be used",source="steps") 
            except:
                logger.warning('Unable to update config')
        else: 
            if CONFIG_STATUS is None or CONFIG_STATUS != self.version:                
                await self.cbpi.config.add("BoilKettle", BoilKettle, type=ConfigType.KETTLE, description="Define Kettle that is used for Boil, Whirlpool and Cooldown. If not selected, MASH_TUN will be used",source="steps")                 

        if MASH_TUN is None:
            logger.info("INIT MASH_TUN")
            try:
                await self.cbpi.config.add("MASH_TUN", "", type=ConfigType.KETTLE, description="Default Mash Tun",source="steps") 
            except:
                logger.warning('Unable to update config')
        else: 
            if CONFIG_STATUS is None or CONFIG_STATUS != self.version:                
                await self.cbpi.config.add("MASH_TUN", MASH_TUN, type=ConfigType.KETTLE, description="Default Mash Tun",source="steps")                 

       ## Check if CSV logfiles is on config 
        if logfiles is None:
            logger.info("INIT CSV logfiles")
            try:
                await self.cbpi.config.add("CSVLOGFILES", "Yes", type=ConfigType.SELECT, description="Write sensor data to csv logfiles", 
                                                                                                source="craftbeerpi",
                                                                                               options= [{"label": "Yes", "value": "Yes"},
                                                                                                {"label": "No", "value": "No"}])
            except:
                logger.warning('Unable to update config')

       ## Check if influxdb is on config 
        if influxdb is None:
            logger.info("INIT Influxdb")
            try:
                await self.cbpi.config.add("INFLUXDB", "No", type=ConfigType.SELECT, description="Write sensor data to influxdb", 
                                                                                             source="craftbeerpi",
                                                                                              options=  [{"label": "Yes", "value": "Yes"},
                                                                                                {"label": "No", "value": "No"}])
            except:
                logger.warning('Unable to update config')

        ## Check if influxdbaddr is in config
        if influxdbaddr is None:
            logger.info("INIT Influxdbaddr")
            try:
                await self.cbpi.config.add("INFLUXDBADDR", "http://localhost:8086", type=ConfigType.STRING, description="URL Address of your influxdb server (If INFLUXDBCLOUD set to Yes use URL Address of your influxdb cloud server)", source="craftbeerpi")
            except:
                logger.warning('Unable to update config')

        ## Check if influxdbname is in config
        if influxdbname is None:
            logger.info("INIT Influxdbname")
            try:
                await self.cbpi.config.add("INFLUXDBNAME", "cbpi4", type=ConfigType.STRING, description="Name of your influxdb database name (If INFLUXDBCLOUD set to Yes use bucket of your influxdb cloud database)", source="craftbeerpi")
            except:
                logger.warning('Unable to update config')

        ## Check if influxduser is in config
        if influxdbuser is None:
            logger.info("INIT Influxdbuser")
            try:
                await self.cbpi.config.add("INFLUXDBUSER", " ", type=ConfigType.STRING, description="User name for your influxdb database (only if required)(If INFLUXDBCLOUD set to Yes use organisation of your influxdb cloud database)", source="craftbeerpi")
            except:
                logger.warning('Unable to update config')

        ## Check if influxdpwd is in config
        if influxdbpwd is None:
            logger.info("INIT Influxdbpwd")
            try:
                await self.cbpi.config.add("INFLUXDBPWD", " ", type=ConfigType.STRING, description="Password for your influxdb database (only if required)(If INFLUXDBCLOUD set to Yes use token of your influxdb cloud database)", source="craftbeerpi")
            except:
                logger.warning('Unable to update config')

       ## Check if influxdb cloud is on config 
        if influxdbcloud is None:
            logger.info("INIT influxdbcloud")
            try:
                await self.cbpi.config.add("INFLUXDBCLOUD", "No", type=ConfigType.SELECT, description="Write sensor data to influxdb cloud (INFLUXDB must set to Yes)", 
                                                                                                source="craftbeerpi",
                                                                                              options=  [{"label": "Yes", "value": "Yes"},
                                                                                                {"label": "No", "value": "No"}])
            except:
                logger.warning('Unable to update config')

                ## Check if influxdbname is in config
        if influxdbmeasurement is None:
            logger.info("INIT Influxdb measurementname")
            try:
                await self.cbpi.config.add("INFLUXDBMEASUREMENT", "measurement", type=ConfigType.STRING, description="Name of the measurement in your INFLUXDB database (default: measurement)", source="craftbeerpi")
            except:
                logger.warning('Unable to update config')

        if mqttupdate is None:
            logger.info("INIT MQTT update frequency for Kettles and Fermenters")
            try:
                await self.cbpi.config.add("MQTTUpdate", 0, type=ConfigType.SELECT, description="Forced MQTT Update frequency in s for Kettle and Fermenter (no changes in payload required). Restart required after change",
                                                                                                source="craftbeerpi",
                                                                                              options=  [{"label": "30", "value": 30},
                                                                                                {"label": "60", "value": 60},
                                                                                                {"label": "120", "value": 120},
                                                                                                {"label": "300", "value": 300},
                                                                                                {"label": "Never", "value": 0}])
            except:
                logger.warning('Unable to update database')

       ## Check if PRESSURE_UNIT is in config
        if PRESSURE_UNIT is None:
            logger.info("INIT PRESSURE_UNIT")
            try:
                await self.cbpi.config.add("PRESSURE_UNIT", "kPa", type=ConfigType.SELECT, description="Set unit for pressure", 
                                                                                            source="craftbeerpi",
                                                                                             options=   [{"label": "kPa", "value": "kPa"},
                                                                                                {"label": "PSI", "value": "PSI"}])
            except:
                logger.warning('Unable to update config')
        
        # check if SENSOR_LOG_BACKUP_COUNT exists in config
        if SENSOR_LOG_BACKUP_COUNT is None:
            logger.info("INIT SENSOR_LOG_BACKUP_COUNT")
            try:
                await self.cbpi.config.add("SENSOR_LOG_BACKUP_COUNT", 3, type=ConfigType.NUMBER, description="Max. number of backup logs", source="craftbeerpi")
            except:
                logger.warning('Unable to update database')
                
        # check if SENSOR_LOG_MAX_BYTES exists in config
        if SENSOR_LOG_MAX_BYTES is None:
            logger.info("Init maximum size of sensor logfiles")
            try:
                await self.cbpi.config.add("SENSOR_LOG_MAX_BYTES", 100000, type=ConfigType.NUMBER, description="Max. number of bytes in sensor logs", source="craftbeerpi")
            except:
                logger.warning('Unable to update database')
                
        # Check if slow_pipe_animation is in config 
        if slow_pipe_animation is None:
            logger.info("INIT slow_pipe_animation")
            try:
                await self.cbpi.config.add("slow_pipe_animation", "Yes", type=ConfigType.SELECT, description="Slow down dashboard pipe animation taking up close to 100% of the CPU's capacity", 
                                                                                                source="craftbeerpi",
                                                                                               options= [{"label": "Yes", "value": "Yes"},
                                                                                                {"label": "No", "value": "No"}])
            except:
                logger.warning('Unable to update config')

       ## Check if NOTIFY_ON_ERROR is in config
        if NOTIFY_ON_ERROR is None:
            logger.info("INIT NOTIFY_ON_ERROR")
            try:
                await self.cbpi.config.add("NOTIFY_ON_ERROR", "No", type=ConfigType.SELECT, description="Send Notification on Logging Error", 
                                                                                                source="craftbeerpi",
                                                                                               options= [{"label": "Yes", "value": "Yes"},
                                                                                                {"label": "No", "value": "No"}])
            except:
                logger.warning('Unable to update config')

       ## Check if PLAY_BUZZER is in config
        if PLAY_BUZZER is None:
            logger.info("INIT PLAY_BUZZER")
            try:
                await self.cbpi.config.add("PLAY_BUZZER", "No", type=ConfigType.SELECT, description="Play buzzer sound in Web interface on Notifications", 
                                                                                                source="craftbeerpi",
                                                                                               options= [{"label": "Yes", "value": "Yes"},
                                                                                                {"label": "No", "value": "No"}])
            except:
                logger.warning('Unable to update config')

        if BoilAutoTimer is None:
            logging.info("INIT BoilAutoTimer")
            try:
                await self.cbpi.config.add('BoilAutoTimer', 'No', type=ConfigType.SELECT, 
                                            description='Start Boil timer automatically if Temp does not change for 5 Minutes and is above 95C/203F',  
                                                                                                source="steps",                                                                                               
                                                                                               options= [{"label": "Yes", "value": "Yes"},
                                                                                                {"label": "No", "value": "No"}])
                                                                                                
                BoilAutoTimer = self.cbpi.config.get("BoilAutoTimer", "No")
            except:
                logging.warning('Unable to update database')
        else: 
            if CONFIG_STATUS is None or CONFIG_STATUS != self.version:
                await self.cbpi.config.add('BoilAutoTimer', BoilAutoTimer, type=ConfigType.SELECT, 
                                            description='Start Boil timer automatically if Temp does not change for 5 Minutes and is above 95C/203F',                                                                                                 
                                                                                                source="steps",
                                                                                                options=[{"label": "Yes", "value": "Yes"},
                                                                                                {"label": "No", "value": "No"}])
                                                                                                


        ## Check if influxdbname is in config
        if CONFIG_STATUS is None or CONFIG_STATUS != self.version:
            logger.warning("Setting Config Status")
            try:
                await self.cbpi.config.add("CONFIG_STATUS", self.version, type=ConfigType.STRING, description="Status of the config file. Internal use for maintenance", source="hidden")
            except:
                logger.warning('Unable to update config')


def setup(cbpi):
    cbpi.plugin.register("ConfigUpdate", ConfigUpdate)
    pass
