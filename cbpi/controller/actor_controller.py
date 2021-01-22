from cbpi.controller.basic_controller import BasicController
import logging
from tabulate import tabulate
class ActorController(BasicController):

    def __init__(self, cbpi):

        
        super(ActorController, self).__init__(cbpi, "actor.json")
        
    async def on(self, id):
        try:
            item = self.find_by_id(id)
            instance = item.get("instance")
            await instance.on()
        except Exception as e:
            logging.error("Faild to switch on Actor {} {}".format(id, e))

    async def off(self, id):
        try:
            item = self.find_by_id(id)
            instance = item.get("instance")
            await instance.off()
        except Exception as e:
            logging.error("Faild to switch on Actor {} {}".format(id, e))

    async def toogle(self, id):
        try:
            item = self.find_by_id(id)
            instance = item.get("instance")
            await instance.toggle()
        except Exception as e:
            logging.error("Faild to switch on Actor {} {}".format(id, e))
            

    def create_dict(self, data):
        try:
            instance = data.get("instance")
            state = state=instance.get_state()
        except Exception as e:
            logging.error("Faild to crate actor dict {} ".format(e))
            state = dict() 
        return dict(name=data.get("name"), id=data.get("id"), type=data.get("type"), state=state,props=data.get("props", []))