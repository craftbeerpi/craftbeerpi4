from aiohttp import web
from cbpi.api import *

class StepHttpEndpoints():

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.controller = cbpi.step
        self.cbpi.register(self, "/step2")

    def create_dict(self, data):
        return dict(name=data["name"], id=data["id"], type=data.get("type"), status=data["status"],props=data["props"], state_text=data["instance"].get_state())


    @request_mapping(path="/", auth_required=False)
    async def http_get_all(self, request):

        """
        ---
        description: Get all steps
        tags:
        - Step
        responses:
            "200":
                description: successful operation
        """
        return web.json_response(data=self.controller.get_state())
    
    @request_mapping(path="/", method="POST", auth_required=False)
    async def http_add(self, request):

        """

        ---
        description: Add
        tags:
        - Step
        parameters:
        - in: body
          name: body
          description: Created an step
          required: true
          schema:
            type: object
        responses:
            "200":
                description: successful operation
        """

        data = await request.json()
        result = await self.controller.add(data)
        return web.json_response(self.create_dict(result))
    
    @request_mapping(path="/{id}", method="PUT", auth_required=False)
    async def http_update(self, request):

        """
        ---
        description: Update
        tags:
        - Step
        parameters:
        - in: body
          name: body
          description: Created an kettle
          required: false
          schema:
            type: object
        responses:
            "200":
                description: successful operation
        """
        
        data = await request.json()
        id = request.match_info['id']
        result = await self.controller.update(id, data)
        print("RESULT", result)
        return web.json_response(self.create_dict(result))

    @request_mapping(path="/{id}", method="DELETE", auth_required=False)
    async def http_delete(self, request):
        """

        ---
        description: Delete
        tags:
        - Step
        responses:
            "204":
                description: successful operation
        """
        id = request.match_info['id']
        await self.controller.delete(id)
        return web.Response(status=204)

    @request_mapping(path="/next", method="POST", auth_required=False)
    async def http_next(self, request):
        """

        ---
        description: Next
        tags:
        - Step
        responses:
            "204":
                description: successful operation
        """
        
        await self.controller.next()
        return web.Response(status=204)


    @request_mapping(path="/move", method="PUT", auth_required=False)
    async def http_move(self, request):
        
        """
        ---
        description: Move
        tags:
        - Step
        parameters:
        - in: body
          name: body
          description: Created an kettle
          required: false
          schema:
            type: object
            properties:
              id:
                type: string
              direction:
                type: "integer"
                format: "int64"
        responses:
            "204":
                description: successful operation
        """
        data = await request.json()
        await self.controller.move(data["id"], data["direction"])
        return web.Response(status=204)

    @request_mapping(path="/start", method="POST", auth_required=False)
    async def http_start(self, request):
        
        """
        ---
        description: Move
        tags:
        - Step
        responses:
            "204":
                description: successful operation
        """
        
        await self.controller.start()
        return web.Response(status=204)

    @request_mapping(path="/stop", method="POST", auth_required=False)
    async def http_stop(self, request):
        
        """

        ---
        description: Stop Step
        tags:
        - Step
        responses:
            "204":
                description: successful operation
        """
        
        await self.controller.stop()
        return web.Response(status=204)


    @request_mapping(path="/reset", method="POST", auth_required=False)
    async def http_reset(self, request):
        
        """

        ---
        description: Move
        tags:
        - Step
        responses:
            "204":
                description: successful operation
        """
        
        await self.controller.reset_all()
    
        return web.Response(status=204)

    @request_mapping(path="/basic", method="PUT", auth_required=False)
    async def http_save_basic(self, request):
        
        """

        ---
        description: Move
        tags:
        - Step
        responses:
            "204":
                description: successful operation
        """
        data = await request.json()
        await self.controller.save_basic(data)
    
        return web.Response(status=204)
        