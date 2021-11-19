from cbpi.api.dataclasses import Kettle, Props
from cbpi.controller.basic_controller2 import BasicController
import logging
from tabulate import tabulate
class KettleController(BasicController):

    def __init__(self, cbpi):
        super(KettleController, self).__init__(cbpi, Kettle, "kettle.json")
        self.update_key = "kettleupdate"
        self.autostart = False
    
    def create(self, data):
        return Kettle(data.get("id"), data.get("name"), type=data.get("type"), props=Props(data.get("props", {})), sensor=data.get("sensor"), heater=data.get("heater"), agitator=data.get("agitator"))

    async def toggle(self, id):
        
        try:
            item = self.find_by_id(id)
            
            if item.instance is None or item.instance.state == False: 
                await self.start(id)
            else:
                await item.instance.stop()
            await self.push_udpate()
        except Exception as e:
            logging.error("Failed to switch on KettleLogic {} {}".format(id, e))

    async def set_target_temp(self, id, target_temp):
        try:
            item = self.find_by_id(id)
            item.target_temp = target_temp
            await self.save()
        except Exception as e:
            logging.error("Failed to set Target Temp {} {}".format(id, e))

    async def stop(self, id):
        try:
            logging.info("Stop Kettele {}".format(id))
            item = self.find_by_id(id)
            await item.instance.stop()
            await self.push_udpate()
        except Exception as e:
            logging.error("Failed to switch off KettleLogic {} {}".format(id, e))
