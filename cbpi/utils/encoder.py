from json import JSONEncoder


class ComplexEncoder(JSONEncoder):

    def default(self, obj):
        try:

            if hasattr(obj, "to_json") and callable(getattr(obj, "to_json")):
                return obj.to_json()
            else:
                raise TypeError()
        except Exception as e:
            print(e)
            pass
        return None
