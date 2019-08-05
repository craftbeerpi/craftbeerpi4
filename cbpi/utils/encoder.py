import datetime
from json import JSONEncoder


class ComplexEncoder(JSONEncoder):

    def default(self, obj):
        try:

            if hasattr(obj, "to_json") and callable(getattr(obj, "to_json")):
                return obj.to_json()
            elif isinstance(obj, datetime.datetime):
                return obj.__str__()
            else:
                raise TypeError()
        except Exception as e:
            print(e)
            pass
        return None
