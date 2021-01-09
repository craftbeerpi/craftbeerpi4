from aiohttp import web
from cbpi.api import *
from voluptuous import Schema

from cbpi.http_endpoints.http_curd_endpoints import HttpCrudEndpoints
from cbpi.utils import json_dumps


class DashBoardHttpEndpoints(HttpCrudEndpoints):

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.controller = cbpi.dashboard
        self.cbpi.register(self, "/dashboard")

    @request_mapping(path="/", auth_required=False)
    async def http_get_all(self, request):
        """

        ---
        description: Get all dashboards
        tags:
        - Dashboard
        responses:
            "200":
                description: successful operation
        """
        return await super().http_get_all(request)

    @request_mapping(path="/{id:\d+}", auth_required=False)
    async def http_get_one(self, request):
        """
        ---
        description: Get one Dashboard by id
        tags:
        - Dashboard
        parameters:
        - name: "id"
          in: "path"
          description: "Actor ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "200":
                description: successful operation
        """
        return await super().http_get_one(request)

    @request_mapping(path="/", method="POST", auth_required=False)
    async def http_add(self, request):
        """
        ---
        description: Create a new Dashboard
        tags:
        - Dashboard
        parameters:
        - in: body
          name: body
          description: Create a new Dashboard
          required: false
          schema:
            type: object
            properties:
              name:
                type: string
        responses:
            "200":
                description: successful operation
        """

        return await super().http_add(request)

    @request_mapping(path="/{id:\d+}", method="PUT", auth_required=False)
    async def http_update(self, request):
        """
        ---
        description: Update a Dashboard
        tags:
        - Dashboard
        parameters:
        - name: "id"
          in: "path"
          description: "Dashboard ID"
          required: true
          type: "integer"
          format: "int64"
        - in: body
          name: body
          description: Update a dashboard
          required: false
          schema:
            type: object
            properties:
              name:
                type: string
        responses:
            "200":
                description: successful operation
        """
        return await super().http_update(request)

    @request_mapping(path="/{id:\d+}", method="DELETE", auth_required=False)
    async def http_delete_one(self, request):
        """
        ---
        description: Delete a Dashboard
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
            "204":
                description: successful operation
        """
        id = request.match_info['id']
        await self.cbpi.dashboard.delete_dashboard(id)
        return web.Response(status=204)

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
