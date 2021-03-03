from enum import Enum

class ConfigType(Enum):
    STRING = "string"
    NUMBER = "number"
    SELECT = "select"
    KETTLE = "kettle"
    ACTOR = "actor"
    SENSOR = "sensor"


