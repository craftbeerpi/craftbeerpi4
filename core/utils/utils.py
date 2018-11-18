from pprint import pprint


from core.api.property import Property
from core.utils.encoder import ComplexEncoder

__all__ = ['load_config',"json_dumps", "parse_props"]

import json
from json import JSONEncoder

import yaml

from core.database.model import DBModel, ActorModel


def load_config(fname):
    try:
        with open(fname, 'rt') as f:
            data = yaml.load(f)
        return data
    except:
        pass




def json_dumps(obj):
    return json.dumps(obj, cls=ComplexEncoder)




def parse_props(self, cls):
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




