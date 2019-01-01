import logging
import os

from aiohttp import web
from cbpi_api import request_mapping
from cbpi_api.exceptions import CBPiException

from core.controller.crud_controller import CRUDController
from core.database.model import ConfigModel
from utils import load_config, json_dumps
from cbpi_api.config import ConfigType

class ConfigHTTPController():
    @request_mapping(path="/{name}/", method="POST", auth_required=False)
    async def http_post(self, request) -> web.Response:
        """
        ---
        description: Set config parameter
        tags:
        - Config
        parameters:
        - name: "name"
          in: "path"
          description: "Parameter name"
          required: true
          type: "string"
        responses:
            "204":
                description: successful operation
        """
        name = request.match_info['name']
        data = await request.json()
        print(data)
        await self.set(name=name, value=data.get("value"))
        return web.Response(status=204)

    @request_mapping(path="/", auth_required=False)
    async def http_get_all(self, request) -> web.Response:
        """
        ---
        description: Get all config parameters
        tags:
        - Config
        responses:
            "200":
                description: successful operation
        """
        return web.json_response(self.cache, dumps=json_dumps)

    @request_mapping(path="/{name}/", auth_required=False)
    async def http_paramter(self, request) -> web.Response:
        """
        ---
        description: Get all config parameters
        tags:
        - Config
        parameters:
        - name: "name"
          in: "path"
          description: "Parameter name"
          required: true
          type: "string"
        responses:
            "200":
                description: successful operation
        """
        name = request.match_info['name']
        if name not in self.cache:
            raise CBPiException("Parameter %s not found" % name)

        return web.json_response(self.cache.get(name), dumps=json_dumps)

class ConfigController(ConfigHTTPController):

    '''
    The main actor controller
    '''
    model = ConfigModel

    def __init__(self, cbpi):
        self.cache = {}
        self.logger = logging.getLogger(__name__)
        self.cbpi = cbpi
        self.cbpi.register(self, "/config")

    async def init(self):
        this_directory = os.path.dirname(__file__)
        self.static = load_config(os.path.join(this_directory, '../../config/config.yaml'))
        items = await self.model.get_all()
        for key, value in items.items():
            self.cache[value.name] = value


    def get(self, name, default=None):
        self.logger.info("GET CONFIG VALUE %s (default %s)" % (name,default))
        if name in self.cache and self.cache[name].value is not None:
            return self.cache[name].value
        else:
            return default

    async def set(self, name, value):
        self.logger.debug("SET %s = %s" % (name, value))
        if name in self.cache:

            self.cache[name].value = value
            m = await self.model.update(**self.cache[name].__dict__)
            await self.cbpi.bus.fire(topic="config/%s/update" % name, name=name, value=value)


    async def add(self, name, value, type: ConfigType, description, options=None):
        m = await self.model.insert(name=name, value=value, type=type.value, description=description, options=options)
        await self.cbpi.bus.fire(topic="config/%s/add" % name, name=name, value=value)
