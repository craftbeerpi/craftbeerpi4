__all__ = ['load_config',"json_dumps"]

import json
from json import JSONEncoder

import yaml

from core.database.model import DBModel, ActorModel


def load_config(fname):
    with open(fname, 'rt') as f:
        data = yaml.load(f)
    return data


class ComplexEncoder(JSONEncoder):
    def default(self, obj):

        try:
            if isinstance(obj, DBModel):
                return obj.__dict__

            elif isinstance(obj, ActorModel):
                return None

            elif hasattr(obj, "callback"):
                return obj()
            else:
                return None
        except TypeError as e:
            pass
        return None


def json_dumps(obj):
    return json.dumps(obj, cls=ComplexEncoder)
