__all__ = ["CBPiException","KettleException","SensorException","ActorException"]


class CBPiException(Exception):
    pass

class KettleException(CBPiException):
    pass

class SensorException(CBPiException):
    pass

class ActorException(CBPiException):
    pass