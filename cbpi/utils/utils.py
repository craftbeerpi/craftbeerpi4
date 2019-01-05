from cbpi.utils.encoder import ComplexEncoder

__all__ = ['load_config',"json_dumps"]

import json
import yaml


def load_config(fname):
    try:
        with open(fname, 'rt') as f:
            data = yaml.load(f)
        return data
    except Exception as e:
        pass

def json_dumps(obj):
    return json.dumps(obj, cls=ComplexEncoder)
