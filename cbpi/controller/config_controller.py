import logging
import os

from cbpi.api.config import ConfigType
from cbpi.database.model import ConfigModel
from cbpi.utils import load_config


class ConfigController:
    '''
    The main actor controller
    '''
    model = ConfigModel

    def __init__(self, cbpi):
        self.cache = {}
        self.logger = logging.getLogger(__name__)
        self.cbpi = cbpi
        self.cbpi.register(self)


    def get_state(self):
        return self.cache

    async def init(self):
        this_directory = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2])
        
        self.static = load_config("{}/config/config.yaml".format(this_directory))
        items = await self.model.get_all()
        for key, value in items.items():
            self.cache[value.name] = value

    def get(self, name, default=None):
        self.logger.debug("GET CONFIG VALUE %s (default %s)" % (name, default))
        if name in self.cache and self.cache[name].value is not None:
            print("name", self.cache[name].value)
            return self.cache[name].value
        else:
            return default

    async def set(self, name, value):
        self.logger.debug("SET %s = %s" % (name, value))
        if name in self.cache:
            self.cache[name].value = value
            await self.model.update(**self.cache[name].__dict__)
            await self.cbpi.bus.fire(topic="config/%s/update" % name, name=name, value=value)

    async def add(self, name, value, type: ConfigType, description, options=None):
        await self.model.insert(name=name, value=value, type=type.value, description=description, options=options)
        await self.cbpi.bus.fire(topic="config/%s/add" % name, name=name, value=value)
