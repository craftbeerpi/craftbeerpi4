from aiohttp import web
from cbpi_api import request_mapping
from cbpi_api.exceptions import CBPiException

from http_endpoints.http_curd_endpoints import HttpCrudEndpoints
from utils import json_dumps


class ConfigHttpEndpoints(HttpCrudEndpoints):

    def __init__(self, cbpi):
        super().__init__(cbpi)
        self.controller = cbpi.config
        self.cbpi.register(self, "/config")

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
        await self.controller.set(name=name, value=data.get("value"))
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
        return web.json_response(self.controller.cache, dumps=json_dumps)

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