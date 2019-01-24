from aiohttp import web
from cbpi.api import *


from cbpi.http_endpoints.http_curd_endpoints import HttpCrudEndpoints
auth = False


class KettleHttpEndpoints(HttpCrudEndpoints):
    @request_mapping(path="/types", auth_required=False)
    async def get_types(self, request):
        return await super().get_types(request)

    @request_mapping(path="/", auth_required=False)
    async def http_get_all(self, request):
        """
        ---
        description: Get all kettles
        tags:
        - Kettle
        responses:
            "204":
                description: successful operation
        """
        return await super().http_get_all(request)

    @request_mapping(path="/{id:\d+}", auth_required=False)
    async def http_get_one(self, request):
        """
        ---
        description: Get Kettle by Id
        tags:
        - Kettle
        parameters:
        - name: "id"
          in: "path"
          description: "Actor ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
        """
        return await super().http_get_one(request)

    @request_mapping(path="/", method="POST", auth_required=False)
    async def http_add(self, request):
        """
        ---
        description: add a kettle
        tags:
        - Kettle
        parameters:
        - in: body
          name: body
          description: Created an kettle
          required: false
          schema:
            type: object
            properties:
              name:
                type: string
              sensor:
                type: "integer"
                format: "int64"
              heater:
                type: "integer"
                format: "int64"
              agitator:
                type: "integer"
                format: "int64"
              target_temp:
                type: "integer"
                format: "int64"
              logic:
                type: string
              config:
                type: object
        responses:
            "204":
                description: successful operation
        """
        return await super().http_add(request)

    @request_mapping(path="/{id}", method="PUT", auth_required=False)
    async def http_update(self, request):
        """
        ---
        description: Update a kettle
        tags:
        - Kettle
        parameters:
        - name: "id"
          in: "path"
          description: "Kettle ID"
          required: true
          type: "integer"
          format: "int64"
        - in: body
          name: body
          description: Created an kettle
          required: false
          schema:
            type: object
            properties:
              name:
                type: string
              sensor:
                type: "integer"
                format: "int64"
              heater:
                type: "integer"
                format: "int64"
              agitator:
                type: "integer"
                format: "int64"
              target_temp:
                type: "integer"
                format: "int64"
              logic:
                type: string
              config:
                type: object
        responses:
            "204":
                description: successful operation
        """
        return await super().http_update(request)

    @request_mapping(path="/{id}", method="DELETE", auth_required=False)
    async def http_delete_one(self, request):
        """
        ---
        description: Delete a kettle
        tags:
        - Kettle
        parameters:
        - name: "id"
          in: "path"
          description: "kettle ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
        """
        return await super().http_delete_one(request)

    def __init__(self, cbpi):
        super().__init__(cbpi)
        self.controller = cbpi.kettle
        self.cbpi.register(self, "/kettle")

    @request_mapping(path="/{id:\d+}/automatic", method="POST", auth_required=False)
    async def http_automatic(self, request):
        """
        ---
        description: Toggle Automatic
        tags:
        - Kettle
        parameters:
        - name: "id"
          in: "path"
          description: "Kettle ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
        """
        await self.controller.toggle_automtic(int(request.match_info['id']))
        return web.Response(status=204)

    @request_mapping(path="/{id:\d+}/heater/on", auth_required=False)
    async def http_heater_on(self, request):
        """
        ---
        description: Kettle Heater on
        tags:
        - Kettle
        parameters:
        - name: "id"
          in: "path"
          description: "Kettle ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
        """
        await self.controller.heater_on(int(request.match_info['id']))
        return web.Response(status=204)

    @request_mapping(path="/{id:\d+}/heater/off", auth_required=False)
    async def http_heater_off(self, request):
        """
        ---
        description: Kettle Heater off
        tags:
        - Kettle
        parameters:
        - name: "id"
          in: "path"
          description: "Kettle ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
        """
        await self.controller.heater_off(int(request.match_info['id']))
        return web.Response(status=204)

    @request_mapping(path="/{id:\d+}/agitator/on", auth_required=False)
    async def http_agitator_on(self, request):
        """
        ---
        description: Kettle Agitator on
        tags:
        - Kettle
        parameters:
        - name: "id"
          in: "path"
          description: "Kettle ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
        """
        await self.controller.agitator_on(int(request.match_info['id']))
        return web.Response(status=204)

    @request_mapping(path="/{id:\d+}/agitator/off", auth_required=False)
    async def http_agitator_off(self, request):
        """
        ---
        description: Kettle Agitator off
        tags:
        - Kettle
        parameters:
        - name: "id"
          in: "path"
          description: "Kettle ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
        """
        await self.controller.agitator_off(int(request.match_info['id']))
        return web.Response(status=204)

    @request_mapping(path="/{id:\d+}/targettemp", auth_required=False)
    async def http_taget_temp(self, request):
        """
        ---
        description: Get Target Temp of kettle
        tags:
        - Kettle
        parameters:
        - name: "id"
          in: "path"
          description: "Kettle ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
        """
        kettle_id = int(request.match_info['id'])
        temp = await self.controller.get_traget_temp(kettle_id)
        return web.json_response(data=dict(target_temp=temp, kettle_id=kettle_id))

    @request_mapping(path="/{id:\d+}/temp/{temp:\d+}", method="PUT", auth_required=False)
    async def http_set_taget_temp(self, request):
        """
        ---
        description: Get Target Temp of kettle
        tags:
        - Kettle
        parameters:
        - name: "id"
          in: "path"
          description: "Kettle ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
        """
        kettle_id = int(request.match_info['id'])
        target_temp = int(request.match_info['temp'])
        await self.cbpi.bus.fire(topic="kettle/%s/targettemp" % kettle_id, kettle_id=kettle_id, target_temp=target_temp)
        return web.Response(status=204)

    @request_mapping(path="/{id:\d+}/temp", auth_required=False)
    async def http_temp(self, request):
        """
        ---
        description: Get Temp of kettle
        tags:
        - Kettle
        parameters:
        - name: "id"
          in: "path"
          description: "Kettle ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
        """
        kettle_id = int(request.match_info['id'])
        temp = await self.controller.get_temp(kettle_id)

        return web.Response(status=204)

