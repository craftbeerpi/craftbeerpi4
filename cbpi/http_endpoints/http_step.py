from cbpi.controller.step_controller import StepController
from cbpi.api.dataclasses import Props, Step
from aiohttp import web
from cbpi.api import *

class StepHttpEndpoints():

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.controller : StepController = cbpi.step
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
        step = Step(name=data.get("name"), props=Props(data.get("props", {})), type=data.get("type"))
        response_data = await self.controller.add(step)
        return web.json_response(data=response_data.to_dict())


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
        step = Step(id, data.get("name"), Props(data.get("props", {})), data.get("type"))
        return web.json_response((await self.controller.update(step)).to_dict())

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
    
    @request_mapping(path="/action/{id}", method="POST", auth_required=False)
    async def http_call_action(self, request):
        """
        ---
        description: Call action
        tags:
        - Step
        parameters:
        - name: "id"
          in: "path"
          description: "Step id"
          required: true
          type: "integer"
          format: "int64"
        - in: body
          name: body
          description: call action
          required: false
          schema:
            type: object
            properties:
              action:
                type: string
              parameter:
                type: "array"
                items:
                    type: string
        responses:
            "204":
                description: successful operation
        """
        data = await request.json()

        id = request.match_info['id']
        await self.controller.call_action(id,data.get("action"), data.get("parameter",[]))
        return web.Response(status=204)

    @request_mapping(path="/clear", method="POST", auth_required=False)
    async def http_clear(self, request):
        
        """

        ---
        description: Clear ALll
        tags:
        - Step
        responses:
            "204":
                description: successful operation
        """
        
        await self.controller.clear()
        return web.Response(status=204)

    @request_mapping(path="/savetobook", method="POST", auth_required=False)
    async def http_savetobook(self, request):
        
        """

        ---
        description: Save Active Recipe to Recipe Book
        tags:
        - Step
        responses:
            "204":
                description: successful operation
        """
        await self.controller.savetobook()
        return web.Response(status=204)



    
