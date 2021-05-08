import datetime
from json import JSONEncoder

from pandas import Timestamp


class ComplexEncoder(JSONEncoder):
    def default(self, obj):
        try:

            if hasattr(obj, "to_json") and callable(getattr(obj, "to_json")):
                return obj.to_json()
            elif isinstance(obj, datetime.datetime):
                return obj.__str__()
            elif isinstance(obj, Timestamp):
                print("TIMe")
                return obj.__str__()
            else:
                print(type(obj))
                raise TypeError()
        except Exception as e:

            pass
        return None
