import asyncio
import os

from aiohttp import web

from cbpi.api import request_mapping

from cbpi.http_endpoints.http_curd_endpoints import HttpCrudEndpoints


class SensorHttpEndpoints(HttpCrudEndpoints):

    def __init__(self, cbpi):
        super().__init__(cbpi)
        self.controller = cbpi.sensor
        self.cbpi.register(self, "/sensor")

    @request_mapping(path="/types", auth_required=False)
    async def get_types(self, request):
        """
        ---
        description: Get all sensor types
        tags:
        - Sensor
        responses:
            "200":
                description: successful operation
        """
        return await super().get_types(request)

    @request_mapping(path="/", auth_required=False)
    async def http_get_all(self, request):
        """

        ---
        description: Get all sensor
        tags:
        - Sensor
        responses:
            "204":
                description: successful operation
        """
        return await super().http_get_all(request)

    @request_mapping(path="/{id:\d+}", auth_required=False)
    async def http_get_one(self, request):
        """
        ---
        description: Get an sensor
        tags:
        - Sensor
        parameters:
        - name: "id"
          in: "path"
          description: "Sensor ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
            "405":
                description: invalid HTTP Met
        """
        return await super().http_get_one(request)

    @request_mapping(path="/", method="POST", auth_required=False)
    async def http_add(self, request):
        """
        ---
        description: Get one sensor
        tags:
        - Sensor
        parameters:
        - in: body
          name: body
          description: Created an sensor
          required: false
          schema:
            type: object
            properties:
              name:
                type: string
              type:
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
        description: Update an sensor
        tags:
        - Sensor
        parameters:
        - name: "id"
          in: "path"
          description: "Sensor ID"
          required: true
          type: "integer"
          format: "int64"
        - in: body
          name: body
          description: Update an sensor
          required: false
          schema:
            type: object
            properties:
              name:
                type: string
              type:
                type: string
              config:
                type: object
        responses:
            "200":
                description: successful operation
        """
        return await super().http_update(request)

    @request_mapping(path="/{id}", method="DELETE", auth_required=False)
    async def http_delete_one(self, request):
        """
        ---
        description: Delete an sensor
        tags:
        - Sensor
        parameters:
        - name: "id"
          in: "path"
          description: "Sensor ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
        """
        return await super().http_delete_one(request)




    @request_mapping(path="/{id:\d+}/log", auth_required=False)
    async def http_get_log(self, request):
        sensor_id = request.match_info['id']
        resp = web.StreamResponse(status=200, reason='OK', headers={'Content-Type': 'text/html'})

        await resp.prepare(request)
        for filename in sorted(os.listdir("./logs/sensors"), reverse=True):
            if filename.startswith("sensor_%s" % sensor_id):

                with open(os.path.join("./logs/sensors/%s" % filename), 'r') as myfile:
                    await resp.write(str.encode(myfile.read()))
        return resp

    @request_mapping(path="/{id:\d+}/log", method="DELETE", auth_required=False)
    async def http_clear_log(self, request):
        sensor_id = request.match_info['id']

        for filename in sorted(os.listdir("./logs/sensors"), reverse=True):

            if filename == "sensor_%s.log" % sensor_id:
                with open(os.path.join("./logs/sensors/%s" % filename), 'w'):
                    pass
                continue
            if filename.startswith("sensor_%s" % sensor_id):
                os.remove(os.path.join("./logs/sensors/%s" % filename))

        return web.Response(status=204)

    @request_mapping(path="/{id:\d+}/action", method="POST", auth_required=False)
    async def http_action(self, request) -> web.Response:
        """

        ---
        description: Execute action on sensor
        tags:
        - Sensor
        parameters:
        - name: "id"
          in: "path"
          description: "Actor ID"
          required: true
          type: "integer"
          format: "int64"
        - in: body
          name: body
          description: Update an actor
          required: false
          schema:
            type: object
            properties:
              name:
                type: string
              config:
                type: object
        responses:
            "204":
                description: successful operation
        """
        sensor_id = int(request.match_info['id'])

        await self.cbpi.bus.fire(topic="sensor/%s/action" % sensor_id, sensor_id=sensor_id, data=await request.json())
        return web.Response(status=204)