from cbpi.api.dataclasses import Actor
from cbpi.controller.basic_controller2 import BasicController
import logging
from tabulate import tabulate
class ActorController(BasicController):

    def __init__(self, cbpi):
        super(ActorController, self).__init__(cbpi, Actor,"actor.json")
        self.update_key = "actorupdate"


    async def on(self, id):
        try:
            item = self.find_by_id(id)

            if item.instance.state is False:
                await item.instance.on()
                await self.push_udpate()
                await self.cbpi.satellite.publish("cbpi/actor/on", "ACTOR ON")
        except Exception as e:
            logging.error("Faild to switch on Actor {} {}".format(id, e))

    async def off(self, id):
        try:
            item = self.find_by_id(id)
            if item.instance.state is True:
                await item.instance.off()
                await self.push_udpate()
        except Exception as e:
            logging.error("Faild to switch on Actor {} {}".format(id, e))

    async def toogle(self, id):
        try:
            item = self.find_by_id(id)
            instance = item.get("instance")
            await instance.toggle()
        except Exception as e:
            logging.error("Faild to switch on Actor {} {}".format(id, e))
            