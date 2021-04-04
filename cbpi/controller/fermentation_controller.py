
import asyncio
import cbpi
import copy
import json
import logging
import os.path
from os import listdir
from os.path import isfile, join
import shortuuid
from cbpi.api.dataclasses import  Fermenter, FermenterStep, Props, Step
from tabulate import tabulate
import sys, os
from ..api.step import CBPiStep, StepMove, StepResult, StepState



logging.basicConfig(format='%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d:%H:%M:%S',
    level=logging.INFO)

class FermentStep:


    def __init__(self, cbpi, step, on_done) -> None:
        self.cbpi = cbpi
        self.logger = logging.getLogger(__name__)
        self.step = step
        self.props = step.props
        self._done_callback = on_done
        self.task = None
        self.summary = ""

    def _done(self, task):
        if self._done_callback is not None:
            try:
                result = task.result()
                self._done_callback(self, result)
            except Exception as e:
                self.logger.error(e)

    async def run(self):
        while True:
            await asyncio.sleep(1)

    async def _run(self):
        try:
            await self.on_start()
            await self.run()
            self.cancel_reason = StepResult.DONE
        except asyncio.CancelledError as e:
            pass
        finally:
            await self.on_stop()

        return self.cancel_reason

    async def start(self):
        self.logger.info("Start {}".format(self.step.name))
        self.running = True
        self.task = asyncio.create_task(self._run())
        self.task.add_done_callback(self._done)

    async def next(self):
        self.running = False
        self.cancel_reason = StepResult.NEXT
        self.task.cancel()
        await self.task

    async def stop(self):
        try:
            self.running = False
            if self.task is not None and self.task.done() is False:
                self.logger.info("Stopping Task")
                self.cancel_reason = StepResult.STOP
                self.task.cancel()
                await self.task
        except Exception as e:
            self.logger.error(e)
    
    async def on_start(self):
        self.props.hello = "WOOHOo"
        pass

    async def on_stop(self):
        pass
            
class FermenationController:

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.logger = logging.getLogger(__name__)
        self.path = os.path.join(".", 'config', "fermenter_data.json")
        self._loop = asyncio.get_event_loop() 
        self.data = {}
        self.types = {}
        self.cbpi.app.on_cleanup.append(self.shutdown)

    async def shutdown(self, app=None):    
        self.save()
        for fermenter in self.data:
            self.logger.info("Shutdown {}".format(fermenter.name))
            for step in fermenter.steps:
                try:
                    self.logger.info("Stop {}".format(step.name))
                    await step.instance.stop()
                except Exception as e:
                    self.logger.error(e)

    async def load(self):
        if os.path.exists(self.path) is False:
            with open(self.path, "w") as file:
                json.dump(dict(basic={}, steps=[]), file, indent=4, sort_keys=True)
        with open(self.path) as json_file:
            d = json.load(json_file)
            self.data = list(map(lambda item: self._create(item), d))
        
    def _create_step(self, fermenter, item):
        id = item.get("id")
        name = item.get("name")
        status = StepState(item.get("status", "I"))
        type = item.get("type")

        type_cfg = self.types.get(type)
        if type_cfg is not None:
            inst = type_cfg.get("class")()
            print(inst)

        step = FermenterStep(id=id, name=name, type=type, status=status, instance=None, fermenter=fermenter)
        step.instance = FermentStep( self.cbpi, step, self._done)
        return step

    def _done(self, step_instance, result):
        
        step_instance.step.status = StepState.DONE
        self.save()
        if result == StepResult.NEXT:
            asyncio.create_task(self.start(step_instance.step.fermenter.id))

    def _create(self, data):
        id = data.get("id")
        name = data.get("name")
        brewname = data.get("brewname")
        props = Props(data.get("props", {}))
        fermenter = Fermenter(id, name, brewname, props, 0)
        fermenter.steps = list(map(lambda item: self._create_step(fermenter, item), data.get("steps", [])))
        return fermenter
        
    def _find_by_id(self, id):
        return next((item for item in self.data if item.id == id), None)

    async def init(self):
        pass

    async def get_all(self):
        return self.data

    async def get(self, id: str ):
        return self._find_by_id(id)

    async def create(self, data: Fermenter ):
        data.id = shortuuid.uuid()
        self.data.append(data)
        self.save()
        return data

    async def update(self, item: Fermenter ):

        def _update(old_item: Fermenter, item: Fermenter):
            old_item.name = item.name
            old_item.brewname = item.brewname
            old_item.props = item.props
            old_item.target_temp = item.target_temp
            return old_item

        self.data = list(map(lambda old: _update(old, item) if old.id == item.id else old, self.data))
        self.save()
        return item

    async def delete(self, id: str ):
        item = self._find_by_id(id)
        self.data = list(filter(lambda item: item.id != id, self.data))
        self.save()

    def save(self):
        with open(self.path, "w") as file:
            json.dump(list(map(lambda item: item.to_dict(), self.data)), file, indent=4, sort_keys=True)

    async def create_step(self, id, step: Step):
        try:
            step.id = shortuuid.uuid()
            item = self._find_by_id(id)

            step.instance = FermentStep( self.cbpi, step.id, step.name, None, self._done)

            item.steps.append(step)
            self.save()
            return step
        except Exception as e:
            self.logger.error(e)

    async def update_step(self, id, step):
        item = self._find_by_id(id)
        item = list(map(lambda old: item if old.id == step.id else old, item.steps))
        self.save()
    
    async def delete_step(self, id, stepid):
        item = self._find_by_id(id)
        item.steps = list(filter(lambda item: item.id != stepid, item.steps))
        self.save()
    
    def _find_by_status(self, data, status):
        return next((item for item in data if item.status == status), None)

    def _find_step_by_id(self, data, id):
        return next((item for item in data if item.id == id), None)

    async def start(self, id):
        self.logger.info("Start")
        try:
            item = self._find_by_id(id)
            step = self._find_by_status(item.steps, StepState.INITIAL)

            if step is None:
                self.logger.info("No futher step to start")

            await step.instance.start()
            step.status = StepState.ACTIVE
            self.save()
        except Exception as e:
            self.logger.error(e)

    async def stop(self, id):
        try:
            item = self._find_by_id(id)
            step = self._find_by_status(item.steps, StepState.ACTIVE)
            await step.instance.stop()
            step.status = StepState.STOP
            self.save()
        except Exception as e:
            self.logger.error(e)


    async  def next(self, id):
        self.logger.info("Next {} ".format(id))
        try:
            item = self._find_by_id(id)
            step = self._find_by_status(item.steps, StepState.ACTIVE)
            await step.instance.next()
        
        except Exception as e:
            self.logger.error(e)


    async def reset(self, id):
        self.logger.info("Reset")
        try:
            item = self._find_by_id(id)
            for step in item.steps:
                self.logger.info("Stopping Step {} {}".format(step.name, step.id))
                try:
                    await step.instance.stop()
                    step.status = StepState.INITIAL
                except Exception as e:
                    self.logger.error(e)
            self.save()
        except Exception as e:
            self.logger.error(e)

    async def move_step(self, fermenter_id, step_id, direction):
        try:
            fermenter = self._find_by_id(fermenter_id)
            index = next((i for i, item in enumerate(fermenter.steps) if item.id == step_id), None)
            if index == None:
                return 
            if index == 0 and direction == -1:
                return
            if index == len(fermenter.steps)-1 and direction == 1:
                return

            fermenter.steps[index], fermenter.steps[index+direction] = fermenter.steps[index+direction], fermenter.steps[index]
            self.save()
        
        except Exception as e:
            self.logger.error(e)
        

