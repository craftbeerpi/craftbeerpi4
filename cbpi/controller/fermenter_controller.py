from cbpi.api.dataclasses import Fermenter, Props
from cbpi.controller.basic_controller2 import BasicController
import logging
from tabulate import tabulate
class FermenterController(BasicController):

    def __init__(self, cbpi):
        super(FermenterController, self).__init__(cbpi, Fermenter, "fermenter.json")
        self.update_key = "fermenterupdate"
        self.autostart = False
    
    def create(self, data):
        return Fermenter(data.get("id"), data.get("name"), type=data.get("type"), props=Props(data.get("props", {})), sensor=data.get("sensor"), cooler=data.get("cooler"))

    async def toggle(self, id):
        
        try:
            item = self.find_by_id(id)
            
            if item.instance is None or item.instance.state == False: 
                await self.start(id)
            else:
                await item.instance.stop()
            await self.push_udpate()
        except Exception as e:
            logging.error("Faild to switch on FermenterLogic {} {}".format(id, e))

    async def set_target_temp(self, id, target_temp):
        try:
            item = self.find_by_id(id)
            item.target_temp = target_temp
            await self.save()
        except Exception as e:
            logging.error("Faild to set Target Temp {} {}".format(id, e))

