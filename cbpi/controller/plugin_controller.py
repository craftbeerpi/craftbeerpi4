
import importlib
import logging
import os
import pkgutil

from importlib import import_module

from cbpi.api import *
from cbpi.utils.utils import load_config
from importlib_metadata import metadata, version

logger = logging.getLogger(__name__)

class PluginController():
    modules = {}
    types = {}

    def __init__(self, cbpi):
        self.cbpi = cbpi

    def load_plugins(self):

        this_directory = os.sep.join(
            os.path.abspath(__file__).split(os.sep)[:-1])
        for filename in os.listdir(os.path.join(this_directory, "../extension")):
            if os.path.isdir(
                    os.path.join(this_directory, "../extension/") + filename) is False or filename == "__pycache__":
                continue
            try:
                logger.info("Trying to load plugin %s" % filename)
                data = load_config(os.path.join(
                    this_directory, "../extension/%s/config.yaml" % filename))
                if (data.get("active") is True and data.get("version") == 4):
                    self.modules[filename] = import_module(
                        "cbpi.extension.%s" % (filename))
                    self.modules[filename].setup(self.cbpi)
                    # logger.info("Plugin %s loaded successful" % filename)
                else:
                    logger.warning(
                        "Plugin %s is not supporting version 4" % filename)

            except Exception as e:

                logger.error(e)

    def load_plugins_from_evn(self):

        discovered_plugins = {
            name: importlib.import_module(name)
            for finder, name, ispkg
            in pkgutil.iter_modules()
            if name.startswith('cbpi') and len(name) > 4
        }

        for key, value in discovered_plugins.items():
            from importlib.metadata import version
            try:
                logger.info("Try to load plugin:  {} == {} ".format(
                    key, version(key)))
                value.setup(self.cbpi)
                logger.info("Plugin {} loaded successfully".format(key))
            except Exception as e:
                logger.error("FAILED to load plugin {} ".format(key))
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
            self.cbpi.actor.types[name] = self._parse_step_props(clazz, name)

        if issubclass(clazz, CBPiKettleLogic):
            self.cbpi.kettle.types[name] = self._parse_step_props(clazz, name)

        if issubclass(clazz, CBPiFermenterLogic):
            self.cbpi.fermenter.types[name] = self._parse_step_props(
                clazz, name)

        if issubclass(clazz, CBPiSensor):
            self.cbpi.sensor.types[name] = self._parse_step_props(clazz, name)

        if issubclass(clazz, CBPiStep):
            self.cbpi.step.types[name] = self._parse_step_props(clazz, name)

        if issubclass(clazz, CBPiFermentationStep):
            self.cbpi.fermenter.steptypes[name] = self._parse_step_props(
                clazz, name)

        if issubclass(clazz, CBPiExtension):
            self.c = clazz(self.cbpi)

    def _parse_property_object(self, p):
        if isinstance(p, Property.Number):
            return {"label": p.label, "type": "number", "configurable": p.configurable, "description": p.description,
                    "default_value": p.default_value}
        elif isinstance(p, Property.Text):
            return {"label": p.label, "type": "text", "configurable": p.configurable, "default_value": p.default_value,
                    "description": p.description}
        elif isinstance(p, Property.Select):
            return {"label": p.label, "type": "select", "configurable": True, "options": p.options,
                    "description": p.description}
        elif isinstance(p, Property.Actor):
            return {"label": p.label, "type": "actor", "configurable": p.configurable, "description": p.description}
        elif isinstance(p, Property.Sensor):
            return {"label": p.label, "type": "sensor", "configurable": p.configurable, "description": p.description}
        elif isinstance(p, Property.Kettle):
            return {"label": p.label, "type": "kettle", "configurable": p.configurable, "description": p.description}
        elif isinstance(p, Property.Fermenter):
            return {"label": p.label, "type": "fermenter", "configurable": p.configurable, "description": p.description}

    def _parse_step_props(self, cls, name):

        result = {"name": name, "class": cls, "properties": [], "actions": []}

        if hasattr(cls, "cbpi_parameters"):
            parameters = []
            for p in cls.cbpi_parameters:
                parameters.append(self._parse_property_object(p))
            result["properties"] = parameters
        for method_name, method in cls.__dict__.items():
            if hasattr(method, "action"):
                key = method.__getattribute__("key")
                parameters = []
                for p in method.__getattribute__("parameters"):
                    parameters.append(self._parse_property_object(p))
                result["actions"].append(
                    {"method": method_name, "label": key, "parameters": parameters})

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
                    {"name": m, "label": t.label, "type": "number", "configurable": t.configurable,
                     "description": t.description, "default_value": t.default_value})
            elif isinstance(tmpObj.__getattribute__(m), Property.Text):
                t = tmpObj.__getattribute__(m)
                result["properties"].append(
                    {"name": m, "label": t.label, "type": "text", "configurable": t.configurable,
                     "default_value": t.default_value, "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), Property.Select):
                t = tmpObj.__getattribute__(m)
                result["properties"].append(
                    {"name": m, "label": t.label, "type": "select", "configurable": True, "options": t.options,
                     "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), Property.Actor):
                t = tmpObj.__getattribute__(m)
                result["properties"].append(
                    {"name": m, "label": t.label, "type": "actor", "configurable": t.configurable,
                     "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), Property.Sensor):
                t = tmpObj.__getattribute__(m)
                result["properties"].append(
                    {"name": m, "label": t.label, "type": "sensor", "configurable": t.configurable,
                     "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), Property.Kettle):
                t = tmpObj.__getattribute__(m)
                result["properties"].append(
                    {"name": m, "label": t.label, "type": "kettle", "configurable": t.configurable,
                     "description": t.description})
            elif isinstance(tmpObj.__getattribute__(m), Property.Fermenter):
                t = tmpObj.__getattribute__(m)
                result["properties"].append(
                    {"name": m, "label": t.label, "type": "fermenter", "configurable": t.configurable,
                     "description": t.description})

        for method_name, method in cls.__dict__.items():
            if hasattr(method, "action"):
                key = method.__getattribute__("key")
                parameters = method.__getattribute__("parameters")
                result["actions"].append(
                    {"method": method_name, "label": key, "parameters": parameters})

        return result

    async def load_plugin_list(self, filter="cbpi"):
        result = []
        try:
            discovered_plugins = {
                name: importlib.import_module(name)
                for finder, name, ispkg
                in pkgutil.iter_modules()
                if name.startswith(filter) and len(name) > 4
            }
            for key, module in discovered_plugins.items():
                from importlib.metadata import version
                try:
                    from importlib.metadata import (distribution, metadata,
                                                    version)
                    meta = metadata(key)
                    result.append({row: meta[row]
                                  for row in list(metadata(key))})
                except Exception as e:
                    logger.error("FAILED to load plugin {} ".format(key))
                    logger.error(e)

        except Exception as e:
            logger.error(e)
            return []
        return result
    
    async def load_plugin_names(self, filter="cbpi"):
        result = []
        result.append(dict(label="All", value="All"))
        result.append(dict(label="craftbeerpi", value="craftbeerpi"))
        result.append(dict(label="steps", value="steps"))
        try:
            discovered_plugins = {
            name: importlib.import_module(name)
            for finder, name, ispkg
            in pkgutil.iter_modules()
            if name.startswith('cbpi') and len(name) > 4
            }
            for key, module in discovered_plugins.items():
                try:
                    meta = metadata(key)
                    if meta["Name"] != "cbpi4gui" and meta["Keywords"] == "globalsettings":
                        result.append(dict(label=meta["Name"], value=meta["Name"]))
                            
                except Exception as e:
                    logger.error("FAILED to load plugin {} ".format(key))
                    logger.error(e)
        except Exception as e:
            logger.error(e)
            return result
        return result
