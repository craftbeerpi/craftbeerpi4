from cbpi.controller.kettle_controller import KettleController
from cbpi.api.dataclasses import Kettle, Props
from aiohttp import web
from cbpi.api import *

auth = False

class KettleHttpEndpoints():

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.controller : KettleController = cbpi.kettle
        self.cbpi.register(self, "/kettle")

    @request_mapping(path="/", auth_required=False)
    async def http_get_all(self, request):
        """

        ---
        description: Switch actor on
        tags:
        - Kettle
        responses:
            "204":
                description: successful operation
        """
        return web.json_response(data=self.controller.get_state())
        

    @request_mapping(path="/", method="POST", auth_required=False)
    async def http_add(self, request):
        """
        ---
        description: add one Actor
        tags:
        - Kettle
        parameters:
        - in: body
          name: body
          description: Created an actor
          required: true
          
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
              type:
                type: string
              props:
                type: object
            example: 
              name: "Kettle 1"
              type: "CustomKettleLogic"
              props: {}
              
        responses:
            "204":
                description: successful operation
        """
        data = await request.json()
        
        kettle = Kettle(name=data.get("name"), sensor=data.get("sensor"), heater=data.get("heater"), agitator=data.get("agitator"), props=Props(data.get("props", {})), type=data.get("type"))
        response_data = await self.controller.add(kettle)
        return web.json_response(data=response_data.to_dict())
        

    @request_mapping(path="/{id}", method="PUT", auth_required=False)
    async def http_update(self, request):
        """
        ---
        description: Update an actor
        tags:
        - Kettle
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
                props: object
        responses:
            "200":
                description: successful operation
        """
        id = request.match_info['id']
        data = await request.json()
        kettle = Kettle(id=id, name=data.get("name"), sensor=data.get("sensor"), heater=data.get("heater"), agitator=data.get("agitator"), props=Props(data.get("props", {})), type=data.get("type"))
        return web.json_response(data=(await self.controller.update(kettle)).to_dict())
    
    @request_mapping(path="/{id}", method="DELETE", auth_required=False)
    async def http_delete_one(self, request):
        """
        ---
        description: Delete an actor
        tags:
        - Kettle
        parameters:
        - name: "id"
          in: "path"
          description: "Actor ID"
          required: true
          type: "string"
        responses:
            "204":
                description: successful operation
        """
        id = request.match_info['id']
        await self.controller.delete(id)
        return web.Response(status=204)

    @request_mapping(path="/{id}/on", method="POST", auth_required=False)
    async def http_on(self, request) -> web.Response:
        """

        ---
        description: Switch actor on
        tags:
        - Kettle
        parameters:
        - name: "id"
          in: "path"
          description: "Actor ID"
          required: true
          type: "string"
          
        responses:
            "204":
                description: successful operation
            "405":
                description: invalid HTTP Met
        """
        id = request.match_info['id']
        await self.controller.start(id)
        return web.Response(status=204)

    @request_mapping(path="/{id}/off", method="POST", auth_required=False)
    async def http_off(self, request) -> web.Response:
        """

        ---
        description: Switch actor on
        tags:
        - Kettle

        parameters:
        - name: "id"
          in: "path"
          description: "Actor ID"
          required: true
          type: "string"
          
        responses:
            "204":
                description: successful operation
            "405":
                description: invalid HTTP Met
        """
        id = request.match_info['id']
        await self.controller.off(id)
        return web.Response(status=204)
    
    @request_mapping(path="/{id}/toggle", method="POST", auth_required=False)
    async def http_toggle(self, request) -> web.Response:
        """

        ---
        description: Switch actor on
        tags:
        - Kettle

        parameters:
        - name: "id"
          in: "path"
          description: "Kettle ID"
          required: true
          type: "string"
          
        responses:
            "204":
                description: successful operation
            "405":
                description: invalid HTTP Met
        """
        id = request.match_info['id']
        await self.controller.toggle(id)
        return web.Response(status=204)

    @request_mapping(path="/{id}/action", method="POST", auth_required=auth)
    async def http_action(self, request) -> web.Response:
        """

        ---
        description: Toogle an actor on or off
        tags:
        - Kettle
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
              parameter:
                type: object
        responses:
            "204":
                description: successful operation
        """
        actor_id = request.match_info['id']
        data = await request.json()
        await self.controller.call_action(actor_id, data.get("name"), data.get("parameter"))

        return web.Response(status=204)
    @request_mapping(path="/{id}/target_temp", method="POST", auth_required=auth)
    async def http_target(self, request) -> web.Response:
        """

        ---
        description: Toogle an actor on or off
        tags:
        - Kettle
        parameters:
        - name: "id"
          in: "path"
          description: "Actor ID"
          required: true
          type: "integer"
          format: "int64"
        - in: body
          name: body
          description: Update Temp
          required: true
          schema:
            type: object
            properties:
              temp:
                type: integer
        responses:
            "204":
                description: successful operation
        """
        id = request.match_info['id']
        data = await request.json()
        await self.controller.set_target_temp(id,data.get("temp"))
        return web.Response(status=204)