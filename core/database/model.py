from core.database.orm_framework import DBModel


class ActorModel(DBModel):
    __fields__ = ["name", "type", "config"]
    __table_name__ = "actor"
    __json_fields__ = ["config"]


class SensorModel(DBModel):
    __fields__ = ["name", "type", "config"]
    __table_name__ = "sensor"
    __json_fields__ = ["config"]

class ConfigModel(DBModel):
    __fields__ = ["type", "value", "description", "options"]
    __table_name__ = "config"
    __json_fields__ = ["options"]
    __priamry_key__ = "name"

class KettleModel(DBModel):
    __fields__ = ["name","sensor", "heater", "automatic", "logic", "config", "agitator", "target_temp"]
    __table_name__ = "kettle"
    __json_fields__ = ["config"]