import logging
import asyncio
from cbpi.api import *
from cbpi.api.config import ConfigType
from cbpi.api.base import CBPiBase
from cbpi.controller.fermentation_controller import FermentationController
from cbpi.controller.kettle_controller import KettleController

logger = logging.getLogger(__name__)

class MQTTUtil(CBPiExtension):

    def __init__(self,cbpi):
        self.cbpi = cbpi
        self.kettlecontroller = cbpi.kettle
        self.fermentationcontroller = cbpi.fermenter
        # sensor and actor update is done anyhow during startup
#        self.sensorcontroller = cbpi.sensor
#        self.actorcontroller = cbpi.actor

        self.mqttupdate = int(self.cbpi.config.get("MQTTUpdate", 0))
        if self.mqttupdate != 0:
            self._task = asyncio.create_task(self.run())
            logger.info("INIT MQTTUtil")
        else:
            self._task = asyncio.create_task(self.push_once())

    async def push_once(self):
        # wait some time to ensure that kettlecontroller is started
        await asyncio.sleep(5)
        self.push_update()


    async def run(self):

        while True:
            self.push_update()
            await asyncio.sleep(self.mqttupdate)

    def push_update(self):
#        try:
#            self.actor=self.actorcontroller.get_state()
#            for item in self.actor['data']:
#                self.cbpi.push_update("cbpi/{}/{}".format("actorupdate",item['id']), item)
#        except Exception as e:
#            logging.error(e)
#            pass
#        try:
#            self.sensor=self.sensorcontroller.get_state()
#            for item in self.sensor['data']:
#                self.cbpi.push_update("cbpi/{}/{}".format("sensorupdate",item['id']), item)
#        except Exception as e:
#            logging.error(e)
#            pass
        try:
            self.kettle=self.kettlecontroller.get_state()
            for item in self.kettle['data']:
                self.cbpi.push_update("cbpi/{}/{}".format("kettleupdate",item['id']), item)
        except Exception as e:
            logging.error(e)
            pass
        try:
            self.fermenter=self.fermentationcontroller.get_state()
            for item in self.fermenter['data']:
                self.cbpi.push_update("cbpi/{}/{}".format("fermenterupdate",item['id']), item)
        except Exception as e:
            logging.error(e)
            pass


def setup(cbpi):
    if str(cbpi.static_config.get("mqtt", False)).lower() == "true":
        cbpi.plugin.register("MQTTUtil", MQTTUtil)
    pass
