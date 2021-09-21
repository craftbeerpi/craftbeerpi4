import os, threading, time
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
from cbpi.api import *
from cbpi.api.config import ConfigType
from cbpi.api.base import CBPiBase

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
        cooldown_temp = self.cbpi.config.get("steps_cooldown_temp", None)
        mashin_step = self.cbpi.config.get("steps_mashin", None)
        mash_step = self.cbpi.config.get("steps_mash", None)
        mashout_step = self.cbpi.config.get("steps_mashout", None)
        boil_step = self.cbpi.config.get("steps_boil", None)
        cooldown_step = self.cbpi.config.get("steps_cooldown", None)
        max_dashboard_number = self.cbpi.config.get("max_dashboard_number", None)
        current_dashboard_number = self.cbpi.config.get("current_dashboard_number", None)

        if boil_temp is None:
            logger.info("INIT Boil Temp Setting")
            try:
                await self.cbpi.config.add("steps_boil_temp", default_boil_temp, ConfigType.NUMBER, "Default Boil Temperature for Recipe Creation")
            except:
                logger.warning('Unable to update database')

        if cooldown_sensor is None:
            logger.info("INIT Cooldown Sensor Setting")
            try:
                await self.cbpi.config.add("steps_cooldown_sensor", "", ConfigType.SENSOR, "Alternative Sensor to monitor temperature durring cooldown (if not selected, Kettle Sensor will be used)")
            except:
                logger.warning('Unable to update database')

        if cooldown_temp is None:
            logger.info("INIT Cooldown Temp Setting")
            try:
                await self.cbpi.config.add("steps_cooldown_temp", default_cool_temp, ConfigType.NUMBER, "Cooldown temp will send notification when this temeprature is reached")
            except:
                logger.warning('Unable to update database')

        if cooldown_step is None:
            logger.info("INIT Cooldown Step Type")
            try:
                await self.cbpi.config.add("steps_cooldown", "", ConfigType.STEP, "Cooldown step type")
            except:
                logger.warning('Unable to update database')

        if mashin_step is None:
            logger.info("INIT MashIn Step Type")
            try:
                await self.cbpi.config.add("steps_mashin", "", ConfigType.STEP, "MashIn step type")
            except:
                logger.warning('Unable to update database')

        if mash_step is None:
            logger.info("INIT Mash Step Type")
            try:
                await self.cbpi.config.add("steps_mash", "", ConfigType.STEP, "Mash step type")
            except:
                logger.warning('Unable to update database')

        if mashout_step is None:
            logger.info("INIT MashOut Step Type")
            try:
                await self.cbpi.config.add("steps_mashout", "", ConfigType.STEP, "MashOut step type")
            except:
                logger.warning('Unable to update database')

        if boil_step is None:
            logger.info("INIT Boil Step Type")
            try:
                await self.cbpi.config.add("steps_boil", "", ConfigType.STEP, "Boil step type")
            except:
                logger.warning('Unable to update database')

        if max_dashboard_number is None:
            logger.info("INIT Max Dashboard Numbers for multiple dashboards")
            try:
                await self.cbpi.config.add("max_dashboard_number", 4, ConfigType.SELECT, "Max Number of Dashboards",
                                                                                                [{"label": "1", "value": 1},
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
                await self.cbpi.config.add("current_dashboard_number", 1, ConfigType.NUMBER, "Number of current Dashboard")
            except:
                logger.warning('Unable to update database')

       ## Check if AtuoMode for Steps is in config
        AutoMode = self.cbpi.config.get("AutoMode", None)
        if AutoMode is None:
            logger.info("INIT AutoMode")
            try:
                await self.cbpi.config.add("AutoMode", "Yes", ConfigType.SELECT, "Use AutoMode in steps", 
                                                                                                [{"label": "Yes", "value": "Yes"},
                                                                                                {"label": "No", "value": "No"}])
            except:
                logger.warning('Unable to update config')

        ## Check if AddMashInStep for Steps is in config
        AddMashIn = self.cbpi.config.get("AddMashInStep", None)
        if AddMashIn is None:
            logger.info("INIT AddMashInStep")
            try:
                await self.cbpi.config.add("AddMashInStep", "Yes", ConfigType.SELECT, "Add MashIn Step automatically if not defined in recipe", 
                                                                                                [{"label": "Yes", "value": "Yes"},
                                                                                                {"label": "No", "value": "No"}])
            except:
                logger.warning('Unable to update config')

        ## Check if Brewfather UserID is in config
        bfuserid = self.cbpi.config.get("brewfather_user_id", None)
        if bfuserid is None:
            logger.info("INIT Brewfather User ID")
            try:
                await self.cbpi.config.add("brewfather_user_id", "", ConfigType.STRING, "Brewfather User ID")
            except:
                logger.warning('Unable to update config')

        ## Check if Brewfather API Key is in config
        bfapikey = self.cbpi.config.get("brewfather_api_key", None)
        if bfapikey is None:
            logger.info("INIT Brewfather API Key")
            try:
                await self.cbpi.config.add("brewfather_api_key", "", ConfigType.STRING, "Brewfather API Key")
            except:
                logger.warning('Unable to update config')

        ## Check if Brewfather API Key is in config
        RecipeCreationPath = self.cbpi.config.get("RECIPE_CREATION_PATH", None)
        if RecipeCreationPath is None:
            logger.info("INIT Recipe Creation Path")
            try:
                await self.cbpi.config.add("RECIPE_CREATION_PATH", "upload", ConfigType.STRING, "API path to creation plugin. Default: upload . CHANGE ONLY IF USING A RECIPE CREATION PLUGIN")
            except:
                logger.warning('Unable to update config')

        ## Check if  Kettle for Boil, Whirlpool and Cooldown is in config
        BoilKettle = self.cbpi.config.get("BoilKettle", None)
        if BoilKettle is None:
            logger.info("INIT BoilKettle")
            try:
                await self.cbpi.config.add("BoilKettle", "", ConfigType.KETTLE, "Define Kettle that is used for Boil, Whirlpool and Cooldown. If not selected, MASH_TUN will be used") 
            except:
                logger.warning('Unable to update config')


def setup(cbpi):
    cbpi.plugin.register("ConfigUpdate", ConfigUpdate)
    pass
