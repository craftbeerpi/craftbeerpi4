
import logging
import os.path
import json
import sys, os
import shortuuid
import asyncio

from tabulate import tabulate

class BasicController:

    def __init__(self, cbpi, file):
        self.update_key = ""
        self.name = self.__class__.__name__
        self.cbpi = cbpi
        self.cbpi.register(self)
        self.service = self
        self.types = {}
        self.logger = logging.getLogger(__name__)
        self.data = []
        self.autostart = True
        self._loop = asyncio.get_event_loop() 
        self.path = os.path.join(".", 'config', file)
        self.cbpi.app.on_cleanup.append(self.shutdown)
        
    async def init(self):
        await self.load()
        
    async def load(self):
        logging.info("{} Load ".format(self.name))
        with open(self.path) as json_file:
            data = json.load(json_file)
            self.data  = data["data"]
            if self.autostart is True:
                for d in self.data:
                    logging.info("{} Starting ".format(self.name))
                    await self.start(d.get("id"))
                await self.push_udpate()
        
    async def save(self):
        logging.info("{} Save ".format(self.name))
        data = dict(data=list(map(lambda x: self.create_dict(x), self.data)))
        with open(self.path, "w") as file:
            json.dump(data, file, indent=4, sort_keys=True)
        await self.push_udpate()

    async def push_udpate(self):
        self.cbpi.ws.send(dict(topic=self.update_key, data=list(map(lambda x: self.create_dict(x), self.data))))

    def create_dict(self, data):
        return dict(name=data.get("name"), id=data.get("id"), type=data.get("type"), status=data.get("status"),props=data.get("props", []))

    def find_by_id(self, id):
        return next((item for item in self.data if item["id"] == id), None)
    
    def get_index_by_id(self, id):
        return next((i for i, item in enumerate(self.data) if item["id"] == id), None)

    async def shutdown(self, app):    
        logging.info("{} Shutdown ".format(self.name))
        tasks = []
        for item in self.data:
            if item.get("instance") is not None and item.get("instance").running is True:
                await item.get("instance").stop()
                tasks.append(item.get("instance").task)
        await asyncio.gather(*tasks)
        await self.save()

    async def stop(self, id):
        logging.info("{} Stop Id {} ".format(self.name, id))
        
        try:
            item = self.find_by_id(id)
            instance = item.get("instance")
            await instance.stop()
            print("STOP ACTION")
            await instance.task
            print("STOP ACTION", instance)
            await self.push_udpate()
        except Exception as e:
            logging.error("{} Cant stop {} - {}".format(self.name, id, e))

    async def start(self, id):
        logging.info("{} Start Id {} ".format(self.name, id))
        try:
            item = self.find_by_id(id)
            instance = item.get("instance")
            if instance is not None and instance.running is True:
                logging.warning("{} already running {}".format(self.name, id))
                return 

            type = item["type"]
            clazz = self.types[type]["class"]
            item["instance"] = clazz(self.cbpi, item["id"], item["props"])
            await item["instance"].start()
            item["instance"].task = self._loop.create_task(item["instance"].run())
            logging.info("{} started {}".format(self.name, id))
            
        except Exception as e:
            logging.error("{} Cant start {} - {}".format(self.name, id, e))

    def get_types(self):
        logging.info("{} Get Types".format(self.name))
        result = {}
        for key, value in self.types.items():
            result[key] = dict(name=value.get("name"), properties=value.get("properties"), actions=value.get("actions"))
        return result

    def get_state(self):
        logging.info("{} Get State".format(self.name))
        return {"data": list(map(lambda x: self.create_dict(x), self.data)), "types":self.get_types()}

    async def add(self, data):
        logging.info("{} Add".format(self.name))
        id = shortuuid.uuid()
        item = {**data, "id": id, "instance": None , "name": data.get("name"), "props": data.get("props", {})}
        self.data.append(item)
        if self.autostart is True:
            await self.start(id)
        await self.save()
        return item 

    async def update(self, id, data) -> dict:
        logging.info("{} Get Update".format(self.name))
        await self.stop(id)
        self.data = list(map(lambda old: {**old, **data} if old["id"] == id else old, self.data))
        if self.autostart is True:
            await self.start(id)    
        await self.save()
        return self.find_by_id(id)

    async def delete(self, id) -> None:
        logging.info("{} Delete".format(self.name))
        await self.stop(id)
        self.data = list(filter(lambda x: x["id"] != id, self.data))
        await self.save()

    async def call_action(self, id, action, parameter) -> None:
        
        logging.info("{} call all Action {} {}".format(self.name, id, action))
        try:
            item = self.find_by_id(id)
            
            instance = item.get("instance")
            await instance.__getattribute__(action)(**parameter)
        except Exception as e:
            logging.error("{} Faild to call action on {} {} {}".format(self.name, id, action, e))
