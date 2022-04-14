from cbpi.api.dataclasses import Config
import logging
import os

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
                self.cache[key] = Config(name=value.get("name"), value=value.get("value"), description=value.get("description"), type=ConfigType(value.get("type", "string")), options=value.get("options", None) )

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

    async def add(self, name, value, type: ConfigType, description, options=None):
        self.cache[name] = Config(name,value,description,type,options)
        data = {}
        for key, value in self.cache.items():
            data[key] = value.to_dict()
        with open(self.path, "w") as file:
            json.dump(data, file, indent=4, sort_keys=True)
