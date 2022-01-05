__all__ = ["CBPiException","KettleException","FermenterException","SensorException","ActorException"]


class CBPiException(Exception):
    pass

class KettleException(CBPiException):
    pass

class FermenterException(CBPiException):
    pass

class SensorException(CBPiException):
    pass

class ActorException(CBPiException):
    pass
