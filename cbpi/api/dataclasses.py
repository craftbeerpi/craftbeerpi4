from cbpi.api.config import ConfigType
from enum import Enum
from typing import Any
from cbpi.api.step import StepState
from dataclasses import dataclass

class Props:

    def __init__(self, data={}):
        super(Props, self).__setattr__('__data__', {})
        for key, value in data.items():
            self.__setattr__(key, value)
    def __getattr__(self, name):
        return self.__data__.get(name)
    
    def __setattr__(self, name, value):
        self.__data__[name] = value

    def __str__(self):
        return self.__data__.__str__()


    def __getitem__(self, key):
        return self.__data__[key]

    def __setitem__(self, key, value):
        self.__data__[key] = value

    def __contains__(self, key):
        return key in self.__data__

    def get(self, key, d=None):
        if key in self.__data__:
            return self.__data__[key]
        else:
            return d
        
    def to_dict(self):

        def parse_object(value):
            if isinstance(value, Props):
                return value.to_dict()
            elif isinstance(value, list):
                return list(map(parse_object, value))
            else:
                return value

        return dict((key, parse_object(value)) for (key, value) in self.__data__.items())



@dataclass
class Actor:
    id: str = None
    name: str = None
    props: Props = Props()
    state: bool = False
    type: str = None
    instance: str = None

    def __str__(self):
        return "name={} props={}, state={}, type={}".format(self.name, self.props, self.state, self.type)
    def to_dict(self):
        return dict(id=self.id, name=self.name, type=self.type, props=self.props.to_dict(), state=self.instance.get_state())


@dataclass
class Sensor:
    id: str = None
    name: str = None
    props: Props = Props()
    state: bool = False
    type: str = None
    instance: str = None

    def __str__(self):
        return "name={} props={}, state={}".format(self.name, self.props, self.state)
    def to_dict(self):
        return dict(id=self.id, name=self.name, type=self.type, props=self.props.to_dict(), state=self.state)

@dataclass
class Kettle:
    id: str = None
    name: str = None
    props: Props = Props()
    instance: str = None
    agitator: Actor = None
    heater: Actor = None
    sensor: Sensor = None
    type: str = None
    target_temp: int = 0

    def __str__(self):
        return "name={} props={} temp={}".format(self.name, self.props, self.target_temp)
    def to_dict(self):

        if self.instance is not None:
            
            state = self.instance.state
            print("READ STATE", state)
        else:
            state = False
        return dict(id=self.id, name=self.name, state=state,  target_temp=self.target_temp, heater=self.heater, agitator=self.agitator, sensor=self.sensor, type=self.type, props=self.props.to_dict())

@dataclass
class Fermenter:
    id: str = None
    name: str = None
    props: Props = Props()
    instance: str = None
    cooler: Actor = None
    sensor: Sensor = None
    type: str = None
    target_temp: int = 0

    def __str__(self):
        return "name={} props={} temp={}".format(self.name, self.props, self.target_temp)
    def to_dict(self):

        if self.instance is not None:
            
            state = self.instance.state
            print("READ STATE", state)
        else:
            state = False
        return dict(id=self.id, name=self.name, state=state,  target_temp=self.target_temp, heater=self.cooler, sensor=self.sensor, type=self.type, props=self.props.to_dict())

@dataclass
class Step:
    id: str = None
    name: str = None
    props: Props = Props()
    type: str = None
    status: StepState = StepState.INITIAL
    instance: str = None

    def __str__(self):
        return "name={} props={}, type={}, instance={}".format(self.name, self.props, self.type, self.instance)
    def to_dict(self):

        msg = self.instance.summary if self.instance is not None else ""
        
        return dict(id=self.id, name=self.name, state_text=msg, type=self.type, status=self.status.value, props=self.props.to_dict())



class ConfigType(Enum):
    STRING="string"
    ACTOR="actor"
    SENSOR="sensor"
    KETTLE="kettle"
    FERMENTER="fermenter"
    NUMBER="number"
    SELECT="select"

@dataclass  
class Config:
    
    name: str = None
    value: Any = None
    description: str = None
    type: ConfigType = ConfigType.STRING
    options: Any = None

    def __str__(self):
        return "....name={} value={}".format(self.name, self.value)
    def to_dict(self):  
        return dict(name=self.name, value=self.value, type=self.type.value, description=self.description, options=self.options)