
import logging
import os.path
import json
from cbpi.api.dataclasses import Fermenter, Actor, Props
import sys, os
import shortuuid
import asyncio

from tabulate import tabulate

class BasicController:

    def __init__(self, cbpi, resource, file):
        self.resource = resource
        self.update_key = ""
        self.name = self.__class__.__name__
        self.cbpi = cbpi
        self.cbpi.register(self)
        self.service = self
        self.types = {}
        self.logger = logging.getLogger(__name__)
        self.data = []
        self.autostart = True
        #self._loop = asyncio.get_event_loop() 
        self.path = self.cbpi.config_folder.get_file_path(file)
        self.cbpi.app.on_cleanup.append(self.shutdown)
        
    async def init(self):
        await self.load()
    
    def create(self, data):
        return self.resource(data.get("id"), data.get("name"), type=data.get("type"), props=Props(data.get("props", {})) )

    async def load(self):
        logging.info("{} Load ".format(self.name))
        with open(self.path) as json_file:
            data = json.load(json_file)
            
            for i in data["data"]:
                self.data.append(self.create(i))
   
            if self.autostart is True:
                for item in self.data:
                    logging.info("{} Starting ".format(self.name))
                    await self.start(item.id)
                await self.push_udpate()
        
    async def save(self):
        logging.info("{} Save ".format(self.name))
        data = dict(data=list(map(lambda actor: actor.to_dict(), self.data))) 
        with open(self.path, "w") as file:
            json.dump(data, file, indent=4, sort_keys=True)
        await self.push_udpate()
        
    async def push_udpate(self):
        self.cbpi.ws.send(dict(topic=self.update_key, data=list(map(lambda item: item.to_dict(), self.data))))
        #self.cbpi.push_update("cbpi/{}".format(self.update_key), list(map(lambda item: item.to_dict(), self.data)))
        for item in self.data:
            self.cbpi.push_update("cbpi/{}/{}".format(self.update_key,item.id), item.to_dict())

    def find_by_id(self, id):
        return next((item for item in self.data if item.id == id), None)
    
    def get_index_by_id(self, id):
        return next((i for i, item in enumerate(self.data) if item.id == id), None)

    async def shutdown(self, app):    
        logging.info("{} Shutdown ".format(self.name))
        tasks = []
        for item in self.data:
            if item.instance is not None and item.instance.running is True:
                item.instance.task.cancel()
                tasks.append(item.instance.task)
        await asyncio.gather(*tasks)
        await self.save()

    async def stop(self, id):
        logging.info("{} Stop Id {} ".format(self.name, id))
        try:
            item = self.find_by_id(id)
            await item.instance.stop()
            item.instance.running = False
            await self.push_udpate()
        except Exception as e:
            logging.error("{} Cant stop {} - {}".format(self.name, id, e))

    async def start(self, id):
        logging.info("{} Start Id {} ".format(self.name, id))
        try:
            item = self.find_by_id(id)
            if item.instance is not None and item.instance.running is True:
                logging.warning("{} already running {}".format(self.name, id))
                return 
            if item.type is None:
                logging.warning("{} No Type {}".format(self.name, id))
                return 
            clazz = self.types[item.type]["class"]
            item.instance = clazz(self.cbpi, item.id, item.props)
            
            await item.instance.start()
            item.instance.running = True
            item.instance.task = asyncio.get_event_loop().create_task(item.instance._run())
            #item.instance.task = self._loop.create_task(item.instance._run())
            
            logging.info("{} started {}".format(self.name, id))
            
#            await self.push_udpate()
        except Exception as e:
            logging.error("{} Cant start {} - {}".format(self.name, id, e))

    def get_types(self):
#        logging.info("{} Get Types".format(self.name))
        result = {}
        for key, value in self.types.items():
            result[key] = dict(name=value.get("name"), properties=value.get("properties"), actions=value.get("actions"))
        return result

    def get_state(self):
#        logging.info("{} Get State".format(self.name))
        return {"data": list(map(lambda x: x.to_dict(), self.data)), "types":self.get_types()}

    async def add(self, item):
        logging.info("{} Add".format(self.name))
        item.id = shortuuid.uuid()
        self.data.append(item)
        if self.autostart is True:
            await self.start(item.id)
        await self.save()
        return item 

    async def update(self, item):
        logging.info("{} Get Update".format(self.name))
        await self.stop(item.id)
        
        self.data = list(map(lambda old_item: item if old_item.id == item.id else old_item, self.data))
        if self.autostart is True:
            await self.start(item.id)    
        await self.save()
        return self.find_by_id(item.id)

    async def delete(self, id) -> None:
        logging.info("{} Delete".format(self.name))
        await self.stop(id)
        self.data = list(filter(lambda x: x.id != id, self.data))
        await self.save()

    async def call_action(self, id, action, parameter) -> None:
        logging.info("{} call all Action {} {}".format(self.name, id, action))
        try:
            item = self.find_by_id(id)
            await item.instance.__getattribute__(action)(**parameter)
        except Exception as e:
            logging.error("{} Failed to call action on {} {} {}".format(self.name, id, action, e))
