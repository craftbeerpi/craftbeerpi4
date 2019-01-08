from logging.handlers import RotatingFileHandler
from time import localtime, strftime

from cbpi.api.extension import CBPiExtension
import logging


class CBPiSensor(CBPiExtension):
    def __init__(self, *args, **kwds):
        CBPiExtension.__init__(self, *args, **kwds)
        self.logger = logging.getLogger(__file__)
        self.data_logger = None
        self.state = False



    def log_data(self, value):

        formatted_time = strftime("%Y-%m-%d %H:%M:%S", localtime())

        self.data_logger.debug("%s,%s" % (formatted_time, value))


    def init(self):


        self.data_logger = logging.getLogger('cbpi.sensor.%s' % self.id)
        self.data_logger.propagate = False
        self.data_logger.setLevel(logging.DEBUG)
        handler = RotatingFileHandler('./logs/sensors/sensor_%s.log' % self.id, maxBytes=2000, backupCount=10)
        self.data_logger.addHandler(handler)
        pass


    async def run(self, cbpi):
        self.logger.warning("Sensor Init not implemented")

    def get_state(self):
        pass

    def get_value(self):
        pass