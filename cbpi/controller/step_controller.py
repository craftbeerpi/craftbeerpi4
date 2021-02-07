import asyncio

from tabulate import tabulate
import json
import copy 
import shortuuid
import logging
import os.path

from ..api.step import CBPiStep



class StepController:

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.woohoo = "HALLLO"
        self.logger = logging.getLogger(__name__)
        self.path = os.path.join(".", 'config', "step_data.json")
        self._loop = asyncio.get_event_loop() 
        self.basic_data = {}
        self.step = None
        self.types = {}
        
        self.cbpi.app.on_cleanup.append(self.shutdown)
    
    async def init(self):
        logging.info("INIT STEP Controller")
        self.load(startActive=True)

    def load(self, startActive=False):
        
        # create file if not exists
        if os.path.exists(self.path) is False:
            with open(self.path, "w") as file:
                json.dump(dict(basic={}, profile=[]), file, indent=4, sort_keys=True)

        #load from json file
        with open(self.path) as json_file:
            data = json.load(json_file)
            self.basic_data  = data["basic"]
            self.profile = data["profile"]

        # Start step after start up
        self.profile = list(map(lambda item: {**item, "instance": self.create_step(item.get("id"), item.get("type"), item.get("name"), item.get("props", {}))}, self.profile))
        if startActive is True:
            active_step = self.find_by_status("A")
            if active_step is not None:    
                self._loop.create_task(self.start_step(active_step))

    async def add(self, data):
        logging.info("Add step")
        id = shortuuid.uuid()
        item = {**{"status": "I", "props": {}}, **data, "id": id, "instance": self.create_step(id, data.get("type"), data.get("name"), data.get("props", {}))}
        self.profile.append(item)
        await self.save()
        return item 

    async def update(self, id, data):
        logging.info("update step")
        
        self.profile = list(map(lambda old: {**old, **data} if old["id"] == id else old, self.profile))
        await self.save()
        return self.find_by_id(id)

    async def save(self):
        logging.debug("save profile")
        data = dict(basic=self.basic_data, profile=list(map(lambda x: dict(name=x["name"], type=x.get("type"), id=x["id"], status=x["status"],props=x["props"]), self.profile)))
        with open(self.path, "w") as file:
            json.dump(data, file, indent=4, sort_keys=True)
        await self.push_udpate()

    async def start(self):
        # already running
        if self.find_by_status("A") is not None:
            logging.error("Steps already running")
            return
        # Find next inactive step
        step = self.find_by_status("P")
        if step is not None:
            
            logging.info("Resume step")
            
            await self.start_step(step)
            await self.save()
            return 

        step = self.find_by_status("I")
        if step is not None:
            logging.info("Start Step")
    
            await self.start_step(step)
            await self.save()
            return 

        logging.info("BREWING COMPLETE")
        
    async def next(self):
        logging.info("Trigger Next")
        step = self.find_by_status("A")
        if step is not None:
            instance = step.get("instance")
            if instance is not None:
                logging.info("Next")
                instance.next()
                await instance.task
        else:
            logging.info("No Step is running")
        
    async def resume(self):
        step = self.find_by_status("P")
        if step is not None:
            instance = step.get("instance")
            if instance is not None:
                await self.start_step(step)
        else:
            logging.info("Nothing to resume")

    async def stop(self):
        logging.info("STOP STEP")
        step = self.find_by_status("A")
        if step != None and step.get("instance") is not None:
            logging.info("CALLING STOP STEP")
            instance = step.get("instance")
            instance.stop()
            # wait for task to be finished
            await instance.task
            logging.info("STEP STOPPED")
            step["status"] = "P"
            await self.save()

    async def reset_all(self): 
        step = self.find_by_status("A")
        if step is not None:
            logging.error("Please stop before reset")
            return 
        for item in self.profile:
            logging.info("Reset %s"  % item.get("name"))
            item["status"] = "I"
            await item["instance"].reset()
        await self.push_udpate()

    def create_step(self, id, type, name, props):

        try:
            type_cfg = self.types.get(type)
            clazz = type_cfg.get("class")
            return clazz(self.cbpi, id, name, {**props})
        except:
            pass

    def create_dict(self, data):
        return dict(name=data["name"], id=data["id"], type=data.get("type"), status=data["status"],props=data["props"], state_text=data["instance"].get_state())

    def get_types2(self):
        result = {}
        for key, value in self.types.items():
            result[key] = dict(name=value.get("name"), properties=value.get("properties"), actions=value.get("actions"))
        return result

    def get_state(self):
        return {"basic": self.basic_data, "profile": list(map(lambda x: self.create_dict(x), self.profile)), "types":self.get_types2()}

    async def move(self, id, direction):
        index = self.get_index_by_id(id)
        if direction not in [-1, 1]:
            self.logger.error("Cant move. Direction 1 and -1 allowed")
            return
        self.profile[index], self.profile[index+direction] = self.profile[index+direction], self.profile[index]
        await self.save()
        await self.push_udpate()

    async def delete(self, id):
        step = self.find_by_id(id)
        if step.get("status") == "A":
            logging.error("Cant delete active Step %s", id)
            return 

        self.profile = list(filter(lambda x: x["id"] != id, self.profile))
        await self.save()
        

    async def shutdown(self, app):    
        logging.info("Mash Profile Shutdonw")
        for p in self.profile:
            instance = p.get("instance")
            # Stopping all running task
            if instance.task != None and instance.task.done() is False:
                logging.info("Stop Step")
                instance.stop()
                await instance.task
        await self.save()

    def done(self, task):
        id, reason = task.result()
        if reason == "MAX_EXCEPTIONS":
            step_current = self.find_by_id(id)
            step_current["status"] = "E"
            self._loop.create_task(self.save())
            return

        if reason == "NEXT":
            step_current = self.find_by_status("A")
            if step_current is not None:

                step_current["status"] = "D"
                async def wrapper():
                    ## TODO DONT CALL SAVE
                    await self.save()
                    await self.start()
                self._loop.create_task(wrapper())
            

    def find_by_status(self, status):
        return next((item for item in self.profile if item["status"] == status), None)

    def find_by_id(self, id):
        return next((item for item in self.profile if item["id"] == id), None)
    
    def get_index_by_id(self, id):
        return next((i for i, item in enumerate(self.profile) if item["id"] == id), None)

    async def push_udpate(self):
        self.cbpi.ws.send(dict(topic="step_update", data=list(map(lambda x: self.create_dict(x), self.profile))))
        
    async def start_step(self,step):
        logging.info("Start Step")
        step.get("instance").start()
        step["instance"].task = self._loop.create_task(step["instance"].run())
        step["instance"].task .add_done_callback(self.done)
        step["status"] = "A"

    async def update_props(self, id, props):
        logging.info("SAVE PROPS")
        step = self.find_by_id(id)
        step["props"] = props
        await self.save()
        await self.push_udpate()

    async def save_basic(self, data):
        logging.info("SAVE Basic Data")
        self.basic_data = {**self.basic_data, **data,}
        await self.save()
        await self.push_udpate()
