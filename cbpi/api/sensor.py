import logging
from abc import abstractmethod, ABCMeta
from cbpi.api.extension import CBPiExtension


class CBPiSensor(CBPiExtension, metaclass=ABCMeta):
    def __init__(self, *args, **kwds):
        CBPiExtension.__init__(self, *args, **kwds)
        self.logger = logging.getLogger(__file__)
        self.data_logger = None
        self.state = False

    def get_parameter(self, name, default):
        return self.cbpi.config.get(name, default)


    def log_data(self, value):
        self.cbpi.log.log_data(self.id, value)

    def init(self):
        pass

    async def run(self, cbpi):
        self.logger.warning("Sensor Init not implemented")

    def get_state(self):
        pass

    def get_value(self):
        pass

    def get_unit(self):
        pass

class CBPiSensor2(metaclass=ABCMeta):

    def __init__(self, cbpi, id, props):
        self.cbpi = cbpi
        self.id = id
        self.props = props
        self.logger = logging.getLogger(__file__)
        self.data_logger = None
        self.state = False
        self.running = False

    def init(self):
        pass

    def log_data(self, value):
        self.cbpi.log.log_data(self.id, value)

    @abstractmethod
    async def run(self):
        self.logger.warning("Sensor Init not implemented")

    def get_state(self):
        pass

    def get_value(self):
        pass

    def get_unit(self):
        pass

    async def start(self):
        self.running = True

    async def stop(self):
        
        self.running = False