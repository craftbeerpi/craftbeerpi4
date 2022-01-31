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
        self.kettlecontroller : KettleController = cbpi.kettle
        self.fermentationcontroller : FermentationController = cbpi.fermenter
        self.mqttupdate = int(self.cbpi.config.get("MQTTUpdate", 60))
        if self.mqttupdate != 0:
            self._task = asyncio.create_task(self.run())
            logger.info("INIT MQTTUtil")

    async def run(self):

        while True:
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
            await asyncio.sleep(self.mqttupdate)

def setup(cbpi):
    if str(cbpi.static_config.get("mqtt", False)).lower() == "true":
        cbpi.plugin.register("MQTTUtil", MQTTUtil)
    pass
