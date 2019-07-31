from aiohttp import web
from cbpi.api import *


from cbpi.http_endpoints.http_curd_endpoints import HttpCrudEndpoints


class StepHttpEndpoints(HttpCrudEndpoints):

    def __init__(self, cbpi):
        super().__init__(cbpi)
        self.controller = cbpi.step
        self.cbpi.register(self, "/step")


    @request_mapping(path="/types", auth_required=False)
    async def get_types(self, request):
        """
        ---
        description: Get all step types
        tags:
        - Step
        responses:
            "200":
                description: successful operation
        """
        return await super().get_types(request)

    @request_mapping(path="/", auth_required=False)
    async def http_get_all(self, request):

        """

        ---
        description: Get all steps
        tags:
        - Step
        responses:
            "204":
                description: successful operation
        """
        return await super().http_get_all(request)

    @request_mapping(path="/{id:\d+}", auth_required=False)
    async def http_get_one(self, request):
        """
        ---
        description: Get one step
        tags:
        - Step
        parameters:
        - name: "id"
          in: "path"
          description: "step ID"
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
        description: Get one step
        tags:
        - Step
        parameters:
        - in: body
          name: body
          description: Created an step
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
        description: Update an step
        tags:
        - Step
        parameters:
        - name: "id"
          in: "path"
          description: "step ID"
          required: true
          type: "integer"
          format: "int64"
        - in: body
          name: body
          description: Update an step
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
        description: Delete a step
        tags:
        - Step
        parameters:
        - name: "id"
          in: "path"
          description: "Step ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
        """
        return await super().http_delete_one(request)

    @request_mapping(path="/", method="DELETE", auth_required=False)
    async def http_delete_all(self, request):
        """
        ---
        description: Delete all step
        tags:
        - Step
        responses:
            "204":
                description: successful operation
        """

        await self.cbpi.bus.fire("step/clear")
        return web.Response(status=204)


    @request_mapping(path="/action", method="POST", auth_required=False, json_schema={"action": str, "parameter": dict})
    async def http_action(self, request):
        """
                ---
                description: Call Step Action
                tags:
                - Step
                parameters:
                - in: body
                  name: body
                  description: Step Action
                  required: true
                  schema:
                    type: object
                    properties:
                      action:
                        type: string
                      parameter:
                        type: object
                produces:
                - application/json
                responses:
                    "204":
                        description: successful operation
                    "405":
                        description: invalid HTTP Method
                """
        data = await request.json()
        await self.cbpi.bus.fire("step/action", name=data["action"], parameter=data["parameter"])
        return web.Response(text="OK")

    @request_mapping(path="/start", auth_required=False)
    async def http_start(self, request):
        """
        ---
        description: Start Brewing Process
        tags:
        - Step
        responses:
            "204":
                description: successful operation
        """
        if self.controller.is_running():
            raise CBPiException("Brewing Process Already Running")
        print("FIRE START FROM HTTP")
        await self.cbpi.bus.fire("step/start")
        return web.Response(status=204)


    @request_mapping(path="/reset", auth_required=False)
    async def http_reset(self, request):
        """
        ---
        description: Reset Brewing Process
        tags:
        - Step
        responses:
            "204":
                description: successful operation
        """
        await self.cbpi.bus.fire("step/reset")
        return web.Response(text="OK")

    @request_mapping(path="/next", auth_required=False)
    async def http_next(self, request):
        """
        ---
        description: Start next step
        tags:
        - Step
        responses:
            "204":
                description: successful operation
        """
        await self.cbpi.bus.fire("step/next")
        return web.Response(status=204)

    @request_mapping(path="/stop", auth_required=False)
    async def http_stop(self, request):
        """
        ---
        description: Stop next step
        tags:
        - Step
        responses:
            "204":
                description: successful operation
        """
        await self.cbpi.bus.fire("step/stop")
        return web.Response(status=204)

    @request_mapping(path="/sort", method="POST", auth_required=False)
    async def http_sort(self, request):
        data = await request.json()
        await self.cbpi.bus.fire("step/sort", data=data)
        return web.Response(status=204)