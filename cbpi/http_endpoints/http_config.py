from aiohttp import web
from cbpi.api import *

from cbpi.utils import json_dumps
import logging


class ConfigHttpEndpoints:

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.controller = cbpi.config
        self.cbpi.register(self, "/config")

    @request_mapping(path="/{name}/", method="PUT", auth_required=False)
    async def http_put(self, request) -> web.Response:

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
        - name: body
          in: body
          description: "Parameter Value"
          required: true
          schema:
            type: object
            properties:
              value:
                type: string
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
        return web.json_response(self.controller.get_state(), dumps=json_dumps)

    @request_mapping(path="/{name}/", method="POST", auth_required=False)
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
#        if name not in self.cache:
#            raise CBPiException("Parameter %s not found" % name)
#        data = self.controller.get(name)
        return web.json_response(self.controller.get(name), dumps=json_dumps)

    @request_mapping(path="/remove/{name}/", method="PUT", auth_required=False)
    async def http_remove(self, request) -> web.Response:

        """
        ---
        description: Remove config parameter
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
        await self.controller.remove(name=name)
        return web.Response(status=200)
    
    @request_mapping(path="/getobsolete", auth_required=False)
    async def http_get_obsolete(self, request) -> web.Response:
        """
        ---
        description: Get obsolete config parameters
        tags:
        - Config
        responses:
            "List of Obsolete Parameters":
                description: successful operation
        """
        return web.json_response(await self.controller.obsolete(False), dumps=json_dumps)
    
    @request_mapping(path="/removeobsolete", auth_required=False)
    async def http_remove_obsolete(self, request) -> web.Response:
        """
        ---
        description: Remove obsolete config parameters
        tags:
        - Config
        responses:
            "200":
                description: successful operation
        """
        await self.controller.obsolete(True)
        return web.Response(status=200)