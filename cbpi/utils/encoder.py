from json import JSONEncoder

from cbpi.database.model import ActorModel, SensorModel


class ComplexEncoder(JSONEncoder):

    def default(self, obj):

        from cbpi.database.orm_framework import DBModel

        try:

            if isinstance(obj, ActorModel):


                data = dict(**obj.__dict__)
                data["state"] = obj.instance.get_state()
                del data["instance"]

                return data

            elif isinstance(obj, SensorModel):
                data =  dict(**obj.__dict__)
                data["value"] = value=obj.instance.get_value()
                data["state"] = obj.instance.get_state()
                del data["instance"]
                return data
            #elif callable(getattr(obj, "reprJSON")):
            #    return obj.reprJSON()
            elif isinstance(obj, DBModel):
                return obj.__dict__
            #elif hasattr(obj, "callback"):
            #    return obj()
            else:
                raise TypeError()
        except Exception as e:

            pass
        return None
