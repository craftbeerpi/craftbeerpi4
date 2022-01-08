import asyncio
import cbpi
import copy
import json
import yaml
import logging
import os.path
from os import listdir
from os.path import isfile, join
import shortuuid
from cbpi.api.dataclasses import NotificationAction, Props, Step
from tabulate import tabulate

from ..api.step import StepMove, StepResult, StepState


class StepController:

    def __init__(self, cbpi):
        self.cbpi = cbpi
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


    def create(self, data):
        
        id = data.get("id")
        name = data.get("name")
        type = data.get("type")
        status = StepState(data.get("status", "I"))
        props = Props(data.get("props", {}))

        try:
            type_cfg = self.types.get(type)
            clazz = type_cfg.get("class")
            instance = clazz(self.cbpi, id, name, props, self.done)
        except Exception as e:
            logging.warning("Failed to create step instance %s - %s"  % (id, e))
            instance = None
 
        return Step(id, name, type=type, status=status, instance=instance, props=props )


    def load(self, startActive=False):
        
        # create file if not exists
        if os.path.exists(self.path) is False:
            with open(self.path, "w") as file:
                json.dump(dict(basic={}, steps=[]), file, indent=4, sort_keys=True)

        #load from json file
        with open(self.path) as json_file:
            data = json.load(json_file)
            self.basic_data  = data["basic"]
            self.profile = data["steps"]

        
        # Start step after start up
        self.profile = list(map(lambda item: self.create(item), self.profile))
        if startActive is True:
            active_step = self.find_by_status("A")
            if active_step is not None:     
                self._loop.create_task(self.start_step(active_step))

    async def add(self, item: Step):
        logging.debug("Add step")
        item.id = shortuuid.uuid()
        item.status = StepState.INITIAL
        try:
            type_cfg = self.types.get(item.type)
            clazz = type_cfg.get("class")
            item.instance = clazz(self.cbpi, item.id, item.name, item.props, self.done)
        except Exception as e:
            logging.warning("Failed to create step instance %s - %s "  % (id, e))
            item.instance = None
        self.profile.append(item)
        await self.save()
        return item 

    async def update(self, item: Step):
        
        logging.info("update step")
        try:
            type_cfg = self.types.get(item.type)
            clazz = type_cfg.get("class")
            item.instance = clazz(self.cbpi, item.id, item.name, item.props, self.done)
        except Exception as e:
            logging.warning("Failed to create step instance %s - %s "  % (item.id, e))
            item.instance = None
        
        self.profile = list(map(lambda old: item if old.id == item.id else old, self.profile))
        await self.save()
        return item

    async def save(self):
        logging.debug("save profile")
        data = dict(basic=self.basic_data, steps=list(map(lambda item: item.to_dict(), self.profile)))
        with open(self.path, "w") as file:
            json.dump(data, file, indent=4, sort_keys=True)
        self.push_udpate()

    async def start(self):
        
        if self.find_by_status(StepState.ACTIVE) is not None:
            logging.error("Steps already running")
            return
        
        step = self.find_by_status(StepState.STOP)
        if step is not None:
            logging.info("Resume step")
            self.cbpi.push_update(topic="cbpi/notification", data=dict(type="info", title="Resume", message="Calling resume step"))
            await self.start_step(step)
            await self.save()
            return 

        step = self.find_by_status(StepState.INITIAL)
        if step is not None:
            logging.info("Start Step")
            self.cbpi.push_update(topic="cbpi/notification", data=dict(type="info", title="Start", message="Calling start step"))
            self.push_udpate(complete=True)
            await self.start_step(step)
            await self.save()
            return 
        self.cbpi.notify("Brewing Complete", "Now the yeast will take over",action=[NotificationAction("OK")])
        self.cbpi.push_update(topic="cbpi/notification", data=dict(type="info", title="Brewing completed", message="Now the yeast will take over"))
        logging.info("BREWING COMPLETE")
    
    async def previous(self):
        logging.info("Trigger Next")


    async def next(self):
        logging.info("Trigger Next")
        print("\n\n\n\n")
        print(self.profile)
        print("\n\n\n\n")
        step = self.find_by_status(StepState.ACTIVE)
        if step is not None:
            if step.instance is not None:
                await step.instance.next()

        step = self.find_by_status(StepState.STOP)
        if step is not None:
            if step.instance is not None:
                step.status = StepState.DONE
                await self.save()
                await self.start()
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
        step = self.find_by_status(StepState.ACTIVE)
        if step != None:
            logging.info("CALLING STOP STEP")
            try:
                await step.instance.stop()
                self.cbpi.push_update(topic="cbpi/notification", data=dict(type="info", title="Pause", message="Calling paue step"))
                step.status = StepState.STOP
                
                await self.save()
            except Exception as e:
                logging.error("Failed to stop step - Id: %s" % step.id)

    async def reset_all(self): 
        if self.find_by_status(StepState.ACTIVE) is not None:
            logging.error("Please stop before reset")
            return 

        for item in self.profile:
            logging.info("Reset %s"  % item)
            item.status = StepState.INITIAL
            try:
                await item.instance.reset()
                self.cbpi.push_update(topic="cbpi/notification", data=dict(type="info", title="Stop", message="Calling stop step"))
            except:
                logging.warning("No Step Instance - Id: %s", item.id)
        await self.save()
        self.push_udpate()

    def get_types(self):
        result = {}
        for key, value in self.types.items():
            result[key] = dict(name=value.get("name"), properties=value.get("properties"), actions=value.get("actions"))
        return result

    def get_state(self):
        return {"basic": self.basic_data, "steps": list(map(lambda item: item.to_dict(), self.profile)), "types":self.get_types()}

    async def move(self, id, direction: StepMove):
        index = self.get_index_by_id(id)
        if direction not in [-1, 1]:
            self.logger.error("Cant move. Direction 1 and -1 allowed")
            return
        self.profile[index], self.profile[index+direction] = self.profile[index+direction], self.profile[index]
        await self.save()
        self.push_udpate()

    async def delete(self, id):
        step = self.find_by_id(id)

        if step is None:
            logging.error("Cant find step - Nothing deleted - Id: %s", id)
            return

        if step.status == StepState.ACTIVE:
            logging.error("Cant delete active Step %s", id)
            return 

        self.profile = list(filter(lambda item: item.id != id, self.profile))
        await self.save()
    
    async def shutdown(self, app=None):    
        logging.info("Mash Profile Shutdonw")
        for p in self.profile:
            instance = p.instance
            # Stopping all running task
            if hasattr(instance, "task") and instance.task != None and instance.task.done() is False:
                logging.info("Stop Step")
                await instance.stop()
                await instance.task
        await self.save()
        self.push_udpate()

    def done(self, step, result):       
        if result == StepResult.NEXT:
            step_current = self.find_by_id(step.id)
            step_current.status = StepState.DONE
            async def wrapper():
                await self.save()
                await self.start()
            asyncio.create_task(wrapper())


    def find_by_status(self, status):
        return next((item for item in self.profile if item.status == status), None)

    def find_by_id(self, id):
        return next((item for item in self.profile if item.id == id), None)
    
    def get_index_by_id(self, id):
        return next((i for i, item in enumerate(self.profile) if item.id == id), None)

    def push_udpate(self, complete=False):
        if complete is True:
            self.cbpi.ws.send(dict(topic="mash_profile_update", data=self.get_state()))
            for item in self.profile:
                self.cbpi.push_update(topic="cbpi/stepupdate/{}".format(item.id), data=(item.to_dict()))
        else:
            self.cbpi.ws.send(dict(topic="step_update", data=list(map(lambda item: item.to_dict(), self.profile))))
            step = self.find_by_status(StepState.ACTIVE)
            if step != None:
                self.cbpi.push_update(topic="cbpi/stepupdate/{}".format(step.id), data=(step.to_dict()))

    async def start_step(self,step):
        try:
            logging.info("Try to start step %s" % step)
            await step.instance.start()
            step.status = StepState.ACTIVE
        except Exception as e:
            logging.error("Faild to start step %s" % step)

    async def save_basic(self, data):
        logging.info("SAVE Basic Data")
        self.basic_data = {**self.basic_data, **data,}
        await self.save()
        self.push_udpate()

    async def call_action(self, id, action, parameter) -> None:
        logging.info("Step Controller - call all Action {} {}".format(id, action))
        try:
            item = self.find_by_id(id)
            await item.instance.__getattribute__(action)(**parameter)
        except Exception as e:
            logging.error("Step Controller -Faild to call action on {} {} {}".format(id, action, e))

    async def load_recipe(self, data):
        try:
            await self.shutdown()
        except: 
            pass
        def add_runtime_data(item):
            item["status"] = "I"
            item["id"] = shortuuid.uuid()
        list(map(lambda item: add_runtime_data(item), data.get("steps")))
        with open(self.path, "w") as file:
            json.dump(data, file, indent=4, sort_keys=True)
        self.load()
        self.push_udpate(complete=True)

    async def clear(self):
        try:
            await self.shutdown()
        except: 
            pass
        
        data = dict(basic=dict(), steps=[])
        with open(self.path, "w") as file:
            json.dump(data, file, indent=4, sort_keys=True)
        
        self.load()
        self.push_udpate(complete=True)

    async def savetobook(self):
        name = shortuuid.uuid()
        path = os.path.join(".", 'config', "recipes", "{}.yaml".format(name))
        data = dict(basic=self.basic_data, steps=list(map(lambda item: item.to_dict(), self.profile)))
        with open(path, "w") as file:
            yaml.dump(data, file)
        self.push_udpate()
