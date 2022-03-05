from abc import abstractmethod
import asyncio
import cbpi
import copy
import json
import yaml
import logging
import os.path
import pathlib
from os import listdir
from os.path import isfile, join
import shortuuid
from cbpi.api.dataclasses import  Fermenter, FermenterStep, Props, Step
from cbpi.controller.basic_controller2 import BasicController
from tabulate import tabulate
import sys, os
from ..api.step import CBPiStep, StepMove, StepResult, StepState, CBPiFermentationStep
          
class FermentationController:

    def __init__(self, cbpi):
        self.update_key = "fermenterupdate"
        self.cbpi = cbpi
        self.logger = logging.getLogger(__name__)
        self.path = os.path.join(".", 'config', "fermenter_data.json")
        self.data = []
        self.types = {}
        self.steptypes = {}
        self.cbpi.app.on_cleanup.append(self.shutdown)

    async def init(self):
        logging.info("INIT Fermentation Controller")
        self.check_fermenter_file()
        await self.load()
        pass

    def check_fermenter_file(self):
        if os.path.exists(os.path.join(".", 'config', "fermenter_data.json")) is False:
            logging.info("INIT fermenter_data.json file")
            data = {
                    "data": [
                            ]
                    }
            destfile = os.path.join(".", 'config', "fermenter_data.json")
            json.dump(data,open(destfile,'w'),indent=4, sort_keys=True)
        
        pathlib.Path(os.path.join(".", 'config/fermenterrecipes')).mkdir(parents=True, exist_ok=True)

    async def shutdown(self, app=None, fermenterid=None):    
        self.save()
        if (fermenterid == None):
            for fermenter in self.data:
                self.logger.info("Shutdown {}".format(fermenter.name))
                for step in fermenter.steps:
                    try:
                        self.logger.info("Stop {}".format(step.name))
                        try:
                            step.instance.shutdown = True
                        except:
                            pass
                        await step.instance.stop()
                    except Exception as e:
                        self.logger.error(e)
        else:
            fermenter = self._find_by_id(fermenterid)
            self.logger.info("Shutdown {}".format(fermenter.name))
            for step in fermenter.steps:
                try:
                    self.logger.info("Stop {}".format(step.name))
                    try:
                        step.instance.shutdown = True
                    except:
                        pass
                    await step.instance.stop()
                except Exception as e:
                    self.logger.error(e)


    async def load(self):
        with open(self.path) as json_file:
            data = json.load(json_file)

            for i in data["data"]:
                self.data.append(self._create(i))
                 
    def _create_step(self, fermenter, item):
        id = item.get("id")
        name = item.get("name")
        props = Props(item.get("props"))
        try:
            endtime = int(item.get("endtime", 0))
        except:
            endtime=0

        status = StepState(item.get("status", "I"))
        if status == StepState.ACTIVE:
            status = StepState("S")
        type = item.get("type")

        try:
            type_cfg = self.steptypes.get(type)
            clazz = type_cfg.get("class")
            instance = clazz(self.cbpi, fermenter, item, props, self._done)
        except Exception as e:
            logging.warning("Failed to create step instance %s - %s"  % (id, e))
            instance = None

        step = FermenterStep(id=id, name=name, fermenter=fermenter, props=props, type=type, status=status, endtime=endtime, instance=instance)
        return step

    def _done(self, step_instance, result, fermenter):
        step_instance.step["status"] = "D"
        self.save()
        if result == StepResult.NEXT:
            asyncio.create_task(self.start(fermenter))

    def _create(self, data):
        try:
            id = data.get("id")
            name = data.get("name")
            sensor = data.get("sensor")
            heater = data.get("heater")
            cooler = data.get("cooler")
            logictype = data.get("type")
            temp = data.get("target_temp")
            brewname = data.get("brewname")
            description = data.get("description")
            props = Props(data.get("props", {}))
            fermenter = Fermenter(id, name, sensor, heater, cooler, brewname, description, props, temp, logictype)
            fermenter.steps = list(map(lambda item: self._create_step(fermenter, item), data.get("steps", [])))
            self.push_update()
            return fermenter
        except:
            return

        
    def _find_by_id(self, id):
         return next((item for item in self.data if item.id == id), None)

    async def get_all(self):
        return list(map(lambda x: x.to_dict(), self.data))
    
    def get_types(self):
        result = {}
        for key, value in self.types.items():
            result[key] = dict(name=value.get("name"), properties=value.get("properties"), actions=value.get("actions"))
        return result

    def get_steptypes(self):
        result = {}
        for key, value in self.steptypes.items():
            result[key] = dict(name=value.get("name"), properties=value.get("properties"), actions=value.get("actions"))
        return result

    def get_state(self):
        if self.data == []:
            pass
        
        return {"data": list(map(lambda x: x.to_dict(), self.data)), "types":self.get_types(), "steptypes":self.get_steptypes()}

    def get_step_state(self, fermenterid=None):
        if self.data == []:
            pass
        fermentersteps=[]
        steplist=list(map(lambda x: x.to_dict(), self.data))
        for fermenter in steplist:
            if fermenterid == fermenter.get("id"):
                fermentersteps={"id": fermenter.get("id"), "steps": fermenter.get("steps")}
        return fermentersteps

    def get_fermenter_steps(self):
        if self.data == []:
            pass
        fermentersteps=[]
        steplist=list(map(lambda x: x.to_dict(), self.data))
        for fermenter in steplist:
            fermenterstep={"id": fermenter.get("id"), "steps": fermenter.get("steps")}
            fermentersteps.append(fermenterstep)
        return fermentersteps

    async def find_step_by_id(self, id):
        actionstep = None
        for item in self.data:
            step = self._find_step_by_id(item.steps, id)
            if step is not None:
                actionstep=step
        return actionstep


    async def get(self, id: str ):
        return self._find_by_id(id)

    async def create(self, data: Fermenter ):
        data.id = shortuuid.uuid()
        self.data.append(data)
        self.save()
        self.push_update()
        return data

    async def update(self, item: Fermenter ):

        def _update(old_item: Fermenter, item: Fermenter):
            old_item.name = item.name
            old_item.sensor = item.sensor
            old_item.heater = item.heater
            old_item.cooler = item.cooler
            old_item.type = item.type
            old_item.brewname = item.brewname
            old_item.description = item.description
            old_item.props = item.props
            old_item.target_temp = item.target_temp
            return old_item

        self.data = list(map(lambda old: _update(old, item) if old.id == item.id else old, self.data))
        self.save()
        self.push_update()
        return item

    async def set_target_temp(self, id: str, target_temp):
        try:
            item = self._find_by_id(id)
            logging.info(item.target_temp)
            if item:
                item.target_temp = target_temp
                self.save()
                self.push_update()
        except Exception as e:
            logging.error("Failed to set Target Temp {} {}".format(id, e))

    async def delete(self, id: str ):
        item = self._find_by_id(id)
        self.data = list(filter(lambda item: item.id != id, self.data))
        self.save()
        self.push_update()

    def save(self):
        data = dict(data=list(map(lambda item: item.to_dict(), self.data))) 
        with open(self.path, "w") as file:
            json.dump(data, file, indent=4, sort_keys=True)

    async def create_step(self, id, item):
        try:
            stepid = shortuuid.uuid()
            props = item.get("props")
            status = StepState("I")
            type = item.get("type")
            name = item.get("name")
            props = Props(item.get("props"))
            fermenter = self._find_by_id(id)

            try:
                type_cfg = self.steptypes.get(type)
                clazz = type_cfg.get("class")
                instance = clazz(self.cbpi, fermenter, item, props, self._done)
            except Exception as e:
                logging.warning("Failed to create step instance %s - %s"  % (id, e))
                instance = None
            step = FermenterStep(id=stepid, name=name, fermenter=fermenter, props=props, type=type, status=status, instance=instance)



            fermenter.steps.append(step)
            self.save()
            self.push_update("fermenterstepupdate")
            return step
        except Exception as e:
            self.logger.error(e)

    async def update_step(self, id, item):
        fermenter = self._find_by_id(id)
        stepid = item.get("id")
        props = item.get("props")
        status = StepState("I")
        type = item.get("type")
        endtime = 0
        name = item.get("name")
        props = Props(item.get("props"))

        logging.info("update step")
        try:
            type_cfg = self.steptypes.get(type)
            logging.info(type_cfg)
            clazz = type_cfg.get("class")
            logging.info(clazz)
            instance = clazz(self.cbpi, fermenter, item, props, self._done)
            logging.info(instance)
        except Exception as e:
            logging.warning("Failed to create step instance %s - %s "  % (item.id, e))
            instance = None
        step = FermenterStep(id=stepid, name=name, fermenter=fermenter, props=props, type=type, status=status, endtime=endtime, instance=instance)

        try:
            fermenter.steps = list(map(lambda old: step if old.id == step.id else old, fermenter.steps))
        except Exception as e:
            logging.info(e)

        self.save()

        self.push_update("fermenterstepupdate")

    async def delete_step(self, id, stepid):
        item = self._find_by_id(id)
        # might require later check if step is active
        item.steps = list(filter(lambda item: item.id != stepid, item.steps))
        self.save()
        self.push_update("fermenterstepupdate")
    
    async def clearsteps(self, id):
        item = self._find_by_id(id)
        # might require later check if step is active
        item.steps = []
        self.save()
        self.push_update("fermenterstepupdate")

    async def update_endtime(self, id, stepid, endtime):
        try:
            item = self._find_by_id(id)
            step = self._find_step_by_id(item.steps, stepid)
            step.endtime = int(endtime)
            self.save()
            self.push_update("fermenterstepupdate")          
        except Exception as e:
            self.logger.error(e)

    def _find_by_status(self, data, status):
        return next((item for item in data if item.status == status), None)

    def _find_step_by_id(self, data, id):
        return next((item for item in data if item.id == id), None)

    async def start(self, id):
        self.logger.info("Start {}".format(id))
        try:
            item = self._find_by_id(id)

            step = self._find_by_status(item.steps, StepState.ACTIVE)
            if step is not None:
                logging.error("Steps already running")
                return

            step = self._find_by_status(item.steps, StepState.STOP)
            if step is not None:
                endtime = step.endtime
                await step.instance.start()
                logging.info("Restarting step {}".format(step.name))
                step.status = StepState.ACTIVE
                self.save()
                self.push_update()
                self.push_update("fermenterstepupdate")
                return                     

            step = self._find_by_status(item.steps, StepState.INITIAL)
            logging.info(step)
            if step is None:
                self.logger.info("No futher step to start")
            else:
                step.instance.endtime = 0 
                await step.instance.start()
                logging.info("Starting step {}".format(step.name))
                step.status = StepState.ACTIVE
                self.save()
                self.push_update()
                self.push_update("fermenterstepupdate")

        except Exception as e:
            self.logger.error(e)

    async def stop(self, id):
        try:
            item = self._find_by_id(id)
            step = self._find_by_status(item.steps, StepState.ACTIVE)
            logging.info(step)
            logging.info(step.status)
            if step != None:
                logging.info("CALLING STOP STEP")
                try:
                    await step.instance.stop()
                    step.status = StepState.STOP
                    self.save()
                except Exception as e:
                    logging.error("Failed to stop fermenterstep - Id: %s" % step.id)
                self.push_update()
                self.push_update("fermenterstepupdate")

        except Exception as e:
            self.logger.error(e)

    async def start_logic(self, id):
        try:
            item = self._find_by_id(id)
            logging.info("{} Start Id {} ".format(item.name, id))
            if item.instance is not None and item.instance.running is True:
                logging.warning("{} already running {}".format(item.name, id))
                return 
            if item.type is None:
                logging.warning("{} No Type {}".format(item.name, id))
                return 
            clazz = self.types[item.type]["class"]
            item.instance = clazz(self.cbpi, item.id, item.props)
            
            await item.instance.start()
            item.instance.running = True
            item.instance.task = asyncio.get_event_loop().create_task(item.instance._run())

            
            logging.info("{} started {}".format(item.name, id))
            
        except Exception as e:
            logging.error("{} Cant start {} - {}".format(item.name, id, e))

    async def toggle(self, id):
        
        try:
            item = self._find_by_id(id)
            
            if item.instance is None or item.instance.state == False: 
                await self.start_logic(id)
            else:
                await item.instance.stop()
            self.push_update()
            
        except Exception as e:
            logging.error("Failed to switch on FermenterLogic {} {}".format(id, e))


    async  def next(self, id):
        self.logger.info("Next {} ".format(id))
        try:
            item = self._find_by_id(id)
            logging.info(item)
            step = self._find_by_status(item.steps, StepState.ACTIVE)
            logging.info(step)
            if step is not None:
                if step.instance is not None:
                    step.status = StepState.DONE
                    await step.instance.next()
        
            step = self._find_by_status(item.steps, StepState.STOP)
            logging.info(step)
            if step is not None:
                if step.instance is not None:
                    logging.info(step)
                    step.status = StepState.DONE
                    logging.info(step)
                    self.save()
                    await self.start(id)
            else:
                logging.info("No Step is running")
            self.push_update()
            self.push_update("fermenterstepupdate")
        
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
                    await step.instance.reset()
                    step.status = StepState.INITIAL
                    step.endtime = 0
                except Exception as e:
                    self.logger.error(e)
            self.save()
            self.push_update()
            self.push_update("fermenterstepupdate")
            
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
            self.push_update()
            self.push_update("fermenterstepupdate")
        
        except Exception as e:
            self.logger.error(e)

    def push_update(self, key="fermenterupdate"):

        if key == self.update_key:
            self.cbpi.ws.send(dict(topic=key, data=list(map(lambda item: item.to_dict(), self.data))))
            
            for item in self.data:
                self.cbpi.push_update("cbpi/{}/{}".format(self.update_key,item.id), item.to_dict())
            pass
        else:
            fermentersteps=self.get_fermenter_steps()
            self.cbpi.ws.send(dict(topic=key, data=fermentersteps))

            # send mqtt update for active femrentersteps
            for fermenter in fermentersteps:
                for step in fermenter['steps']:
                    if step['status'] == 'A':
                        self.cbpi.push_update("cbpi/{}/{}/{}".format(key,fermenter['id'],step['id']), step)
        
    async def call_action(self, id, action, parameter) -> None:
        logging.info("FermenterStep Controller - call Action {} {}".format(id, action))
        try:
            item = await self.find_step_by_id(id)
            logging.info(item)
            await item.instance.__getattribute__(action)(**parameter)
        except Exception as e:
            logging.error("FermenterStep Controller - Failed to call action on {} {} {}".format(id, action, e))
    
    async def savetobook(self, fermenterid):
        name = shortuuid.uuid()
        path = os.path.join(".", 'config', "fermenterrecipes", "{}.yaml".format(name))
        fermenter=self._find_by_id(fermenterid)
        try:
            brewname = fermenter.brewname
            description = fermenter.description
            
        except:
            brewname = ""
            description = ""
        self.basic_data={"name": brewname, "description": description}

        try:
            fermentersteps = fermenter.steps
        except:
            fermentersteps = []
        data = dict(basic=self.basic_data, steps=list(map(lambda item: item.to_dict(), fermentersteps)))
        with open(path, "w") as file:
            yaml.dump(data, file)

    async def load_recipe(self, data, fermenterid, name):
        try:
            await self.shutdown(None, fermenterid)
        except: 
            pass
        fermenter = self._find_by_id(fermenterid)
        def add_runtime_data(item):
            item["status"] = "I"
            item["endtime"] = 0
            item["id"] = shortuuid.uuid()
            item["props"]["Sensor"] = fermenter.sensor
        list(map(lambda item: add_runtime_data(item), data.get("steps")))
        fermenter.description = data['basic']['desc']
        if name is not None:
            fermenter.brewname = name
        else:
            fermenter.brewname = data['basic']['name']
        fermenter.steps=[]
        await self.update(fermenter)
        for item in data.get("steps"):
            await self.create_step(fermenterid, item)  
