import logging
import os
from logging.handlers import TimedRotatingFileHandler

from core.job.aiohttp import get_scheduler_from_app

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
        self.types = {}

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

    async def init(self):
        '''
        This method initializes all actors during startup. It creates actor instances

        :return: 
        '''
        await super(SensorController, self).init()
        print("INIT SENSOR")
        for name, clazz in self.types.items():
            print("Type", name)

        for id, value in self.cache.items():
            if value.type in self.types:
                cfg = value.config.copy()
                cfg.update(dict(cbpi=self.cbpi, id=id, name=value.name))
                clazz = self.types[value.type]["class"];
                self.cache[id].instance = clazz(**cfg)
                scheduler = get_scheduler_from_app(self.cbpi.app)
                self.cache[id].instance.job = await scheduler.spawn(self.cache[id].instance.run(self.cbpi), value.name, "sensor")
        print("------------")

    @background_task(name="test", interval=1)
    async def hallo(self):
        print("AHLLO")
        self.logger.info("WOOHO", extra={"sensor": 1})
