from json import JSONEncoder

class ComplexEncoder(JSONEncoder):

    def default(self, obj):

        from cbpi.database.orm_framework import DBModel

        try:
            if isinstance(obj, DBModel):
                return obj.__dict__
            #elif callable(getattr(obj, "reprJSON")):
            #    return obj.reprJSON()
            #elif isinstance(obj, ActorModel):
            #    return None
            #elif hasattr(obj, "callback"):
            #    return obj()
            else:
                raise TypeError()
        except TypeError:
            pass
        return None
