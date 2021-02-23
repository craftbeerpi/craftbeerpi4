import os

from aiohttp import web
from cbpi.api import *

from cbpi.utils import json_dumps
from voluptuous import Schema


class DashBoardHttpEndpoints:

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.controller = cbpi.dashboard
        self.cbpi.register(self, "/dashboard", os.path.join(".","config", "dashboard", "widgets"))


    @request_mapping(path="/{id:\d+}/content", auth_required=False)
    async def get_content(self, request):
        """
        ---
        description: Get Dashboard Content
        tags:
        - Dashboard
        parameters:
        - name: "id"
          in: "path"
          description: "Dashboard ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "200":
                description: successful operation
        """
        dashboard_id = int(request.match_info['id'])
        return web.json_response(await self.cbpi.dashboard.get_content(dashboard_id), dumps=json_dumps)


    @request_mapping(path="/{id:\d+}/content", method="POST", auth_required=False)
    async def add_content(self, request):
        """
        ---
        description: Add Dashboard Content
        tags:
        - Dashboard
        parameters:
        - name: "id"
          in: "path"
          description: "Dashboard ID"
          required: true
          type: "integer"
          format: "int64"
        - name: body
          in: body
          description: Dashboard Content
          required: true
          schema:
            type: object
            properties:
              elements:
                type: array
              pathes:
                type: array
        responses:
            "200":
                description: successful operation
        """
        data = await request.json()
        dashboard_id = int(request.match_info['id'])
        await self.cbpi.dashboard.add_content(dashboard_id, data)
        return web.Response(status=204)

    @request_mapping(path="/{id:\d+}/content", method="DELETE", auth_required=False)
    async def delete_conent(self, request):
        """
        ---
        description: Add Dashboard Content
        tags:
        - Dashboard
        parameters:
        - name: "id"
          in: "path"
          description: "Dashboard ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "200":
                description: successful operation
        """
  
        dashboard_id = int(request.match_info['id'])
        await self.cbpi.dashboard.delete_content(dashboard_id)
        return web.Response(status=204)

    @request_mapping(path="/widgets", method="GET", auth_required=False)
    async def get_custom_widgets(self, request):
        """
        ---
        description: Get Custom Widgets
        tags:
        - Dashboard
        responses:
            "200":
                description: successful operation
        """
  
      
        return web.json_response(await self.cbpi.dashboard.get_custom_widgets(), dumps=json_dumps)
      
