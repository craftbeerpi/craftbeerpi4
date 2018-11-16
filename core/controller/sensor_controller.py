import logging
import os
from logging.handlers import TimedRotatingFileHandler

from core.api.decorator import background_task
from core.controller.crud_controller import CRUDController
from core.database.model import SensorModel
from core.http_endpoints.http_api import HttpAPI


class SensorController(CRUDController, HttpAPI):

    model = SensorModel

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.cbpi.register(self, "/sensor")
        self.service = self

        self.sensors = {"S1": "S1", "S2": "S2"}

        this_directory = os.path.dirname(__file__)
        # __file__ is the absolute path to the current python file.

        handler = TimedRotatingFileHandler(os.path.join(this_directory, '../../logger.conf'), when="m", interval=1, backupCount=5)
        #handler = RotatingFileHandler("first_logfile.log", mode='a', maxBytes=300, backupCount=2, encoding=None, delay=0)
        formatter = logging.Formatter('%(asctime)s,%(sensor)s,%(message)s')
        handler.setFormatter(formatter)

        self.logger = logging.getLogger("SensorController")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False
        self.logger.addHandler(handler)

    async def pre_get_one(self, id):
        pass



    @background_task(name="test", interval=1)
    async def hallo(self):

        self.logger.info("WOOHO", extra={"sensor": 1})
