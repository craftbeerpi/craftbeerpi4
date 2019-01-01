import json
import logging

from core.controller.crud_controller import CRUDController
from core.database.model import SensorModel
from core.http_endpoints.http_api import HttpAPI
from core.job.aiohttp import get_scheduler_from_app
from core.utils.encoder import ComplexEncoder


class SensorController(CRUDController, HttpAPI):

    model = SensorModel

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.cbpi.register(self, "/sensor")
        self.service = self
        self.types = {}
        self.logger = logging.getLogger(__name__)
        self.sensors = {}

    def info(self):

        return json.dumps(dict(name="SensorController", types=self.types), cls=ComplexEncoder)

    async def init(self):
        '''
        This method initializes all actors during startup. It creates actor instances

        :return: 
        '''
        await super(SensorController, self).init()



        for id, value in self.cache.items():
            if value.type in self.types:
                cfg = value.config.copy()
                cfg.update(dict(cbpi=self.cbpi, id=id, name=value.name))
                clazz = self.types[value.type]["class"];
                self.cache[id].instance = clazz(**cfg)
                scheduler = get_scheduler_from_app(self.cbpi.app)
                self.cache[id].instance.job = await scheduler.spawn(self.cache[id].instance.run(self.cbpi), value.name, "sensor")
            else:
                self.logger.error("Sensor type '%s' not found (Available Sensor Types: %s)" % (value.type, ', '.join(self.types.keys())))

    async def get_value(self, id):
        return self.cache[id].instance.value