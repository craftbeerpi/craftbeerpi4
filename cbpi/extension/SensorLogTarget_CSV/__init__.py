
# -*- coding: utf-8 -*-
import os
from logging.handlers import RotatingFileHandler
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
from cbpi.api import *
from cbpi.api.config import ConfigType
import urllib3
import base64

logger = logging.getLogger(__name__)

class SensorLogTargetCSV(CBPiExtension):

    def __init__(self, cbpi): # called from cbpi on start
        self.cbpi = cbpi
        self.logfiles = self.cbpi.config.get("CSVLOGFILES", "Yes")
        if self.logfiles == "No":
            return # never run()
        self._task = asyncio.create_task(self.run()) # one time run() only


    async def run(self): # called by __init__ once on start if CSV is enabled
        self.listener_ID = self.cbpi.log.add_sensor_data_listener(self.log_data_to_CSV)
        logger.info("CSV sensor log target listener ID: {}".format(self.listener_ID))

    async def log_data_to_CSV(self, cbpi, id:str, value:str, formatted_time, name): # called by log_data() hook from the log file controller
        self.logfiles = self.cbpi.config.get("CSVLOGFILES", "Yes")
        if self.logfiles == "No":
            # We intentionally do not unsubscribe the listener here because then we had no way of resubscribing him without a restart of cbpi
            # as long as cbpi was STARTED with CSVLOGFILES set to Yes this function is still subscribed, so changes can be made on the fly.
            # but after initially enabling this logging target a restart is required.
            return
        if id not in self.cbpi.log.datalogger:
            max_bytes = int(self.cbpi.config.get("SENSOR_LOG_MAX_BYTES", 100000))
            backup_count = int(self.cbpi.config.get("SENSOR_LOG_BACKUP_COUNT", 3))

            data_logger = logging.getLogger('cbpi.sensor.%s' % id)
            data_logger.propagate = False
            data_logger.setLevel(logging.DEBUG)
            handler = RotatingFileHandler(os.path.join(self.cbpi.log.logsFolderPath, f"sensor_{id}.log"), maxBytes=max_bytes, backupCount=backup_count)
            data_logger.addHandler(handler)
            self.cbpi.log.datalogger[id] = data_logger

        self.cbpi.log.datalogger[id].info("%s,%s" % (formatted_time, str(value)))

def setup(cbpi):
    cbpi.plugin.register("SensorLogTargetCSV", SensorLogTargetCSV)
