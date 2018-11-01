import json
from json import JSONEncoder

from core.database.model import DBModel, ActorModel


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