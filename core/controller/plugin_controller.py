import logging
import os
from importlib import import_module
from pprint import pprint

import aiohttp
import yaml
from aiohttp import web

from core.api.actor import CBPiActor
from core.api.decorator import request_mapping
from core.api.extension import CBPiExtension
from core.api.kettle_logic import CBPiKettleLogic
from core.api.property import Property
from core.api.sensor import CBPiSensor
from core.api.step import Step
from core.utils.utils import load_config, json_dumps

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)

class PluginController():

    modules = {}
    types = {}

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.cbpi.register(self, "/plugin")

    @classmethod
    async def load_plugin_list(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://raw.githubusercontent.com/Manuel83/craftbeerpi-plugins/master/plugins.yaml') as resp:

                if(resp.status == 200):

                    data = yaml.load(await resp.text())
                    return data

    async def load_plugins(self):

        for filename in os.listdir("./core/extension"):

            if os.path.isdir("./core/extension/" + filename) is False or filename == "__pycache__":
                continue
            try:

                logger.info("Trying to load plugin %s" % filename)

                data = load_config("./core/extension/%s/config.yaml" % filename)


                if(data.get("version") == 4):

                    self.modules[filename] = import_module("core.extension.%s" % (filename))
                    self.modules[filename].setup(self.cbpi)
                    logger.info("Plugin %s loaded successful" % filename)
                else:
                    logger.warning("Plguin %s is not supporting version 4" % filename)



            except Exception as e:
                logger.error(e)

    @request_mapping(path="/plugins", method="GET", auth_required=False)
    async def get_plugins(self, request):
        """
            ---
            description: Get a list of avialable plugins
            tags:
            - Plugin
            produces:
            - application/json
            responses:
                "200":
                    description: successful operation. Return "pong" text
                "405":
                    description: invalid HTTP Method
            """
        return web.json_response(await self.load_plugin_list(), dumps=json_dumps)



    def register(self, name, clazz) -> None:
        '''
        Register a new actor type
        :param name: actor name
        :param clazz: actor class
        :return: None
        '''
        print("REGISTER", name, clazz)
        if issubclass(clazz, CBPiActor):
            self.cbpi.actor.types[name] = {"class": clazz, "config": self._parse_props(clazz)}


        if issubclass(clazz, CBPiSensor):
            self.cbpi.sensor.types[name] = {"class": clazz, "config": self._parse_props(clazz)}


        if issubclass(clazz, CBPiKettleLogic):
            self.cbpi.kettle.types[name] = {"class": clazz, "config": self._parse_props(clazz)}

        if issubclass(clazz, Step):
            print("NAME", name)
            self.cbpi.step.types[name] = {"class": clazz, "config": self._parse_props(clazz)}

        if issubclass(clazz, CBPiExtension):
            self.c  = clazz(self.cbpi)


    def _parse_props(self, cls):
        print("PARSE", cls)
        name = cls.__name__

        result = {"name": name, "class": cls, "properties": [], "actions": []}

        tmpObj = cls()
        members = [attr for attr in dir(tmpObj) if not callable(getattr(tmpObj, attr)) and not attr.startswith("__")]
        for m in members:
            if isinstance(tmpObj.__getattribute__(m), Property.Number):
                t = tmpObj.__getattribute__(m)
                result["properties"].append(
                    {"name": m, "label": t.label, "type": "number", "configurable": t.configurable, "description": t.description, "default_value": t.default_value})
            elif isinstance(tmpObj.__getattribute__(m), Property.Text):
                t = tmpObj.__getattribute__(m)
                result["properties"].append(
                    {"name": m, "label": t.label, "type": "text", "configurable": t.configurable, "default_value": t.default_value, "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), Property.Select):
                t = tmpObj.__getattribute__(m)
                result["properties"].append(
                    {"name": m, "label": t.label, "type": "select", "configurable": True, "options": t.options, "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), Property.Actor):
                t = tmpObj.__getattribute__(m)
                result["properties"].append({"name": m, "label": t.label, "type": "actor", "configurable": t.configurable, "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), Property.Sensor):
                t = tmpObj.__getattribute__(m)
                result["properties"].append({"name": m, "label": t.label, "type": "sensor", "configurable": t.configurable, "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), Property.Kettle):
                t = tmpObj.__getattribute__(m)
                result["properties"].append({"name": m, "label": t.label, "type": "kettle", "configurable": t.configurable, "description": t.description})

        for method_name, method in cls.__dict__.items():
            if hasattr(method, "action"):
                key = method.__getattribute__("key")
                parameters = method.__getattribute__("parameters")
                result["actions"].append({"method": method_name, "label": key, "parameters": parameters})
        pprint(result, width=200)
