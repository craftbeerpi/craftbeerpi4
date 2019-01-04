from aiohttp import web
from cbpi_api import request_mapping
from cbpi_api.exceptions import CBPiException

from http_endpoints.http_curd_endpoints import HttpCrudEndpoints
auth = False

class ActorHttpEndpoints(HttpCrudEndpoints):

    def __init__(self, cbpi):
        super().__init__(cbpi)
        self.controller = cbpi.actor
        self.cbpi.register(self, "/actor")

    @request_mapping(path="/types", auth_required=False)
    async def get_types(self, request):
        """
        ---
        description: Get all actor types
        tags:
        - Actor
        responses:
            "200":
                description: successful operation
        """
        return await super().get_types(request)

    @request_mapping(path="/", auth_required=False)
    async def http_get_all(self, request):
        """

        ---
        description: Switch actor on
        tags:
        - Actor
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
            "405":
                description: invalid HTTP Met
        """
        return await super().http_get_all(request)

    @request_mapping(path="/{id:\d+}", auth_required=False)
    async def http_get_one(self, request):
        """
        ---
        description: Get one Actor
        tags:
        - Actor
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
            "405":
                description: invalid HTTP Met
        """
        return await super().http_get_one(request)

    @request_mapping(path="/", method="POST", auth_required=False)
    async def http_add(self, request):
        """
        ---
        description: Get one Actor
        tags:
        - Actor
        parameters:
        - in: body
          name: body
          description: Created an actor
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
        description: Update an actor
        tags:
        - Actor
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
        description: Delete an actor
        tags:
        - Actor
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
        return await super().http_delete_one(request)

    @request_mapping(path="/{id:\d+}/on", method="POST", auth_required=auth)
    async def http_on(self, request) -> web.Response:
        """

        ---
        description: Switch actor on
        tags:
        - Actor

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
            "405":
                description: invalid HTTP Met
        """
        actor_id = int(request.match_info['id'])
        result = await self.cbpi.bus.fire(topic="actor/%s/switch/on" % actor_id, actor_id=actor_id, power=99)
        for key, value in result.results.items():
            pass
        return web.Response(status=204)


    @request_mapping(path="/{id:\d+}/off", method="POST", auth_required=auth)
    async def http_off(self, request) -> web.Response:
        """

        ---
        description: Switch actor off
        tags:
        - Actor

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
            "405":
                description: invalid HTTP Met
        """
        actor_id = int(request.match_info['id'])
        await self.cbpi.bus.fire(topic="actor/%s/off" % actor_id, actor_id=actor_id)
        return web.Response(status=204)

    @request_mapping(path="/{id:\d+}/toggle", method="POST", auth_required=auth)
    async def http_toggle(self, request) -> web.Response:
        """

        ---
        description: Toogle an actor on or off
        tags:
        - Actor
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
            "405":
                description: invalid HTTP Met
        """
        actor_id = int(request.match_info['id'])

        await self.cbpi.bus.fire(topic="actor/%s/toggle" % actor_id, actor_id=actor_id)
        return web.Response(status=204)

    @request_mapping(path="/{id:\d+}/action", method="POST", auth_required=auth)
    async def http_action(self, request) -> web.Response:
        """

        ---
        description: Toogle an actor on or off
        tags:
        - Actor
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
        actor_id = int(request.match_info['id'])

        await self.cbpi.bus.fire(topic="actor/%s/action" % actor_id, actor_id=actor_id, data=await request.json())
        return web.Response(status=204)