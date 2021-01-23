import logging
import os
from importlib import import_module
import datetime
import aiohttp
import yaml
import subprocess
import sys
from cbpi.api import *
from cbpi.utils.utils import load_config

logger = logging.getLogger(__name__)


class PluginController():
    modules = {}
    types = {}

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.plugins = load_config("./config/plugin_list.txt")
        if self.plugins is None:
            self.plugins = {}


    async def load_plugin_list(self):
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:2202/list') as resp:
                if (resp.status == 200):
                    data = yaml.load(await resp.text())
                    self.plugins = data
                    return data

    def installed_plugins(self):
        return self.plugins

    async def install(self, package_name):
        async def install(cbpi, plugins, package_name):
            data = subprocess.check_output(
                [sys.executable, "-m", "pip", "install", package_name])
            data = data.decode('UTF-8')
            if package_name not in self.plugins:
                now = datetime.datetime.now()
                self.plugins[package_name] = dict(
                    version="1.0", installation_date=now.strftime("%Y-%m-%d %H:%M:%S"))
                with open('./config/plugin_list.txt', 'w') as outfile:
                    yaml.dump(self.plugins, outfile, default_flow_style=False)
            if data.startswith('Requirement already satisfied'):
                self.cbpi.notify(
                    key="p", message="Plugin already installed ", type="warning")
            else:

                self.cbpi.notify(
                    key="p", message="Plugin installed ", type="success")

        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:2202/get/%s' % package_name) as resp:

                if (resp.status == 200):
                    data = await resp.json()
                    await self.cbpi.job.start_job(install(self.cbpi, self.plugins, data["package_name"]), data["package_name"], "plugins_install")
                    return True
                else:
                    self.cbpi.notify(
                        key="p", message="Failed to install Plugin %s " % package_name, type="danger")
                    return False

    async def uninstall(self, package_name):
        async def uninstall(cbpi, plugins, package_name):
            print("try to uninstall", package_name)
            try:
                data = subprocess.check_output(
                    [sys.executable, "-m", "pip", "uninstall", "-y", package_name])
                data = data.decode('UTF-8')
                if data.startswith("Successfully uninstalled"):
                    cbpi.notify(key="p", message="Plugin %s Uninstalled" %
                                package_name, type="success")
                else:
                    cbpi.notify(key="p", message=data, type="success")
            except Exception as e:
                print(e)

        if package_name in self.plugins:
            print("Uninstall", self.plugins[package_name])
            await self.cbpi.job.start_job(uninstall(self.cbpi, self.plugins, package_name), package_name, "plugins_uninstall")

    def load_plugins(self):

        this_directory = os.path.dirname(__file__)
        for filename in os.listdir(os.path.join(this_directory, "../extension")):
            if os.path.isdir(os.path.join(this_directory, "../extension/") + filename) is False or filename == "__pycache__":
                continue
            try:
                logger.info("Trying to load plugin %s" % filename)
                data = load_config(os.path.join(
                    this_directory, "../extension/%s/config.yaml" % filename))

                if (data.get("active") is True and data.get("version") == 4):
                    self.modules[filename] = import_module(
                        "cbpi.extension.%s" % (filename))
                    self.modules[filename].setup(self.cbpi)
                    #logger.info("Plugin %s loaded successful" % filename)
                else:
                    logger.warning(
                        "Plugin %s is not supporting version 4" % filename)

            except Exception as e:
                print(e)
                logger.error(e)

    def load_plugins_from_evn(self):

        for p in self.plugins:
            logger.debug("Load Plugin %s" % p)
            try:
                logger.info("Try to load plugin:  %s " % p)
                self.modules[p] = import_module(p)
                self.modules[p].setup(self.cbpi)

                #logger.info("Plugin %s loaded successfully" % p)
            except Exception as e:
                logger.error("FAILED to load plugin %s " % p)
                logger.error(e)

    def register(self, name, clazz) -> None:
        '''
        Register a new actor type
        :param name: actor name
        :param clazz: actor class
        :return: None
        '''
        logger.debug("Register %s Class %s" % (name, clazz.__name__))
        
        if issubclass(clazz, CBPiActor):
            self.cbpi.actor.types[name] = self._parse_step_props(clazz,name)

        if issubclass(clazz, CBPiKettleLogic):
            self.cbpi.kettle.types[name] = self._parse_step_props(clazz,name)
    
        if issubclass(clazz, CBPiSensor):
            self.cbpi.sensor.types[name] = self._parse_step_props(clazz,name)

        if issubclass(clazz, CBPiStep):
            self.cbpi.step.types[name] = self._parse_step_props(clazz,name)

        if issubclass(clazz, CBPiExtension):
            self.c = clazz(self.cbpi)


    def _parse_property_object(self, p):
        if isinstance(p, Property.Number):
            return {"label": p.label, "type": "number", "configurable": p.configurable, "description": p.description, "default_value": p.default_value}
        elif isinstance(p, Property.Text):
            return {"label": p.label, "type": "text", "configurable": p.configurable, "default_value": p.default_value, "description": p.description}
        elif isinstance(p, Property.Select):
            return {"label": p.label, "type": "select", "configurable": True, "options": p.options, "description": p.description}
        elif isinstance(p, Property.Actor):
            return {"label": p.label, "type": "actor", "configurable": p.configurable, "description": p.description}
        elif isinstance(p, Property.Sensor):
            return {"label": p.label, "type": "sensor", "configurable": p.configurable, "description": p.description}
        elif isinstance(p, Property.Kettle):
            return {"label": p.label, "type": "kettle", "configurable": p.configurable, "description": p.description}

    def _parse_step_props(self, cls, name):

        result = {"name": name, "class": cls, "properties": [], "actions": []}

        if hasattr(cls, "cbpi_parameters"):
            parameters = []
            for p in cls.cbpi_parameters:
                parameters.append(self._parse_property_object(p))
            result["properties"] = parameters
        for method_name, method in cls.__dict__.items():

            if hasattr(method, "action"):
                print(method_name)
                key = method.__getattribute__("key")
                parameters = []
                for p in  method.__getattribute__("parameters"):
                    parameters.append(self._parse_property_object(p))
                result["actions"].append({"method": method_name, "label": key, "parameters": parameters})

        return result

    def _parse_props(self, cls):

        name = cls.__name__

        result = {"name": name, "class": cls, "properties": [], "actions": []}

        tmpObj = cls(cbpi=None, managed_fields=None)
        members = [attr for attr in dir(tmpObj) if not callable(
            getattr(tmpObj, attr)) and not attr.startswith("__")]
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
                result["properties"].append(
                    {"name": m, "label": t.label, "type": "actor", "configurable": t.configurable, "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), Property.Sensor):
                t = tmpObj.__getattribute__(m)
                result["properties"].append(
                    {"name": m, "label": t.label, "type": "sensor", "configurable": t.configurable, "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), Property.Kettle):
                t = tmpObj.__getattribute__(m)
                result["properties"].append(
                    {"name": m, "label": t.label, "type": "kettle", "configurable": t.configurable, "description": t.description})

        for method_name, method in cls.__dict__.items():
            if hasattr(method, "action"):
                key = method.__getattribute__("key")
                parameters = method.__getattribute__("parameters")
                result["actions"].append(
                    {"method": method_name, "label": key, "parameters": parameters})

        return result
