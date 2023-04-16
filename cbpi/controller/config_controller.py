from cbpi.api.dataclasses import Config
import logging
import os
from pathlib import Path

from cbpi.api.config import ConfigType
from cbpi.utils import load_config
import json

class ConfigController:
    

    def __init__(self, cbpi):
        self.cache = {}
        self.logger = logging.getLogger(__name__)
        self.cbpi = cbpi
        self.cbpi.register(self)
        self.path = cbpi.config_folder.get_file_path("config.json")
        self.path_static = cbpi.config_folder.get_file_path("config.yaml")
        self.logger.info("Config folder path : " + os.path.join(Path(self.cbpi.config_folder.configFolderPath).absolute()))

    def get_state(self):  
        result = {}
        for key, value in self.cache.items():
            result[key] = value.to_dict()
        return result    

    async def init(self):
        self.static = load_config(self.path_static)
        with open(self.path) as json_file:
            data = json.load(json_file)
            for key, value in data.items():
                self.cache[key] = Config(name=value.get("name"), value=value.get("value"), description=value.get("description"), type=ConfigType(value.get("type", "string")), source=value.get("source", "craftbeerpi"), options=value.get("options", None))
        logging.error(self.cache)

    def get(self, name, default=None):
        self.logger.debug("GET CONFIG VALUE %s (default %s)" % (name, default))
        if name in self.cache and self.cache[name].value is not None and self.cache[name].value != "":
            return self.cache[name].value
        else:
            return default

    async def set(self, name, value):
        if name in self.cache:
            
            self.cache[name].value = value

            data = {}
            for key, value in self.cache.items():
                data[key] = value.to_dict()
            with open(self.path, "w") as file:
                json.dump(data, file, indent=4, sort_keys=True)

    async def add(self, name, value, type: ConfigType, description, source="craftbeerpi", options=None):
        self.cache[name] = Config(name,value,description,type,source,options)
        data = {}
        for key, value in self.cache.items():
            data[key] = value.to_dict()
        with open(self.path, "w") as file:
            json.dump(data, file, indent=4, sort_keys=True)

    async def remove(self, name):
        data = {}
        self.testcache={}
        success=False
        for key, value in self.cache.items():
            try:
                if key != name:
                    data[key] = value.to_dict()
                    self.testcache[key] = Config(name=data[key].get("name"), value=data[key].get("value"), description=data[key].get("description"), 
                                                 type=ConfigType(data[key].get("type", "string")), options=data[key].get("options", None), 
                                                source=data[key].get("source", "craftbeerpi") )
                    success=True   
            except Exception as e:
                print(e)
                success=False
        if success == True:
            with open(self.path, "w") as file:
                    json.dump(data, file, indent=4, sort_keys=True)
            self.cache=self.testcache
       
    async def obsolete(self, remove=False):
        result = {}
        for key, value in self.cache.items():
            if (value.source not in ('craftbeerpi','steps','hidden')):
                test = await self.cbpi.plugin.load_plugin_list(value.source)
                if test == []:
                    update=self.get(str(value.source)+'_update')
                    if update:
                        result[str(value.source)+'_update']={"value": update}
                        if remove:
                            await self.remove(str(value.source)+'_update')
                    if remove:
                        await self.remove(key)
                    result[key] = value.to_dict()
        return result    