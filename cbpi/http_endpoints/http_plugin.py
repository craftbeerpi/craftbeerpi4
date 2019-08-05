from aiohttp import web
from cbpi.api import request_mapping
from cbpi.utils import json_dumps


class PluginHttpEndpoints:

    def __init__(self,cbpi):
        self.cbpi = cbpi
        self.cbpi.register(self, url_prefix="/plugin")

    @request_mapping(path="/install/", method="POST", auth_required=False, json_schema={"package_name": str})
    async def install(self, request):
        """
        ---
        description: Install Plugin
        tags:
        - Plugin
        parameters:
        - in: body
          name: body
          description: Install a plugin
          required: true
          schema:
            type: object
            properties:
              package_name:
                type: string
        produces:
        - application/json
        responses:
            "204":
                description: successful operation. Return "pong" text
            "405":
                description: invalid HTTP Method
        """

        data = await request.json()
        return web.Response(status=204) if await self.cbpi.plugin.install(data["package_name"]) is True else web.Response(status=500)

    @request_mapping(path="/uninstall", method="POST", auth_required=False, json_schema={"package_name": str})
    async def uninstall(self, request):
        """
        ---
        description: Uninstall Plugin
        tags:
        - Plugin
        parameters:
        - in: body
          name: body
          description: Uninstall a plugin
          required: true
          schema:
            type: object
            properties:
              package_name:
                type: string
        produces:
        - application/json
        responses:
            "204":
                description: successful operation. Return "pong" text
            "405":
                description: invalid HTTP Method
        """

        data = await request.json()
        return web.Response(status=204) if await self.cbpi.plugin.uninstall(data["package_name"]) is True else web.Response(status=500)


    @request_mapping(path="/list", method="GET", auth_required=False)
    async def list(self, request):
        """
            ---
            description: Get a list of avialable plugins
            tags:
            - Plugin
            produces:
            - application/json
            responses:
                "200":
                    description: successful operation. Return "pong" text
                "405":
                    description: invalid HTTP Method
            """
        return web.json_response(await self.cbpi.plugin.load_plugin_list(), dumps=json_dumps)
