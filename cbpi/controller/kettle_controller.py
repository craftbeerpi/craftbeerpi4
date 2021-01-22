from cbpi.controller.basic_controller import BasicController
import logging
from tabulate import tabulate
class KettleController(BasicController):

    def __init__(self, cbpi):
        super(KettleController, self).__init__(cbpi, "kettle.json")
        self.autostart = False
        
    async def on(self, id):
        try:
            item = self.find_by_id(id)
            instance = item.get("instance")
            await instance.start()
        except Exception as e:
            logging.error("Faild to switch on KettleLogic {} {}".format(id, e))

    async def off(self, id):
        try:
            item = self.find_by_id(id)
            instance = item.get("instance")
            await instance.stop()
        except Exception as e:
            logging.error("Faild to switch on KettleLogic {} {}".format(id, e))

    async def set_target_temp(self, id, target_temp):
        try:
            item = self.find_by_id(id)
            item["target_temp"] = target_temp
            await self.save()
        except Exception as e:
            logging.error("Faild to set Target Temp {} {}".format(id, e))

    def create_dict(self, data):
        try:
            instance = data.get("instance")
            state = dict(state=instance.get_state())
        except Exception as e:
            logging.error("Faild to create KettleLogic dict {} ".format(e))
            state = dict() 
        return dict(name=data.get("name"), id=data.get("id"), type=data.get("type"), sensor=data.get("sensor"), heater=data.get("heater"), agitator=data.get("agitator"), target_temp=data.get("target_temp"), state=state,props=data.get("props", []))