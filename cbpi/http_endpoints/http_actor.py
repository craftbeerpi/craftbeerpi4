from cbpi.api.dataclasses import Actor, Props
from aiohttp import web
from cbpi.api import *
auth = False

class ActorHttpEndpoints():

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.controller = cbpi.actor
        self.cbpi.register(self, "/actor")

    @request_mapping(path="/", auth_required=False)
    async def http_get_all(self, request):
        """

        ---
        description: Switch actor on
        tags:
        - Actor
        responses:
            "204":
                description: successful operation
        """
        return web.json_response(data=self.controller.get_state())

    @request_mapping(path="/{id:\w+}", auth_required=False)
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
            "200":
                description: successful operation
            "404":
                description: Actor not found
        """
        actor = self.controller.find_by_id(request.match_info['id'])
        if (actor is None):
          return web.json_response(status=404)

        return web.json_response(data=actor.to_dict(), status=200)
        

    @request_mapping(path="/", method="POST", auth_required=False)
    async def http_add(self, request):
        """
        ---
        description: add one Actor
        tags:
        - Actor
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
              type:
                type: string
              props:
                type: object
            example: 
              name: "Actor 1"
              type: "CustomActor"
              props: {}
              
        responses:
            "204":
                description: successful operation
        """
        data = await request.json()
        actor = Actor(name=data.get("name"), props=Props(data.get("props", {})), type=data.get("type"))
        response_data = await self.controller.add(actor)

        return web.json_response(data=response_data.to_dict())
        

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
                props: object
        responses:
            "200":
                description: successful operation
        """
        id = request.match_info['id']
        data = await request.json()
        actor = Actor(id=id, name=data.get("name"), props=Props(data.get("props", {})), type=data.get("type"))
        return web.json_response(data=(await self.controller.update(actor)).to_dict())
    
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
        - Actor

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
        await self.controller.on(id)
        return web.Response(status=204)

    @request_mapping(path="/{id}/off", method="POST", auth_required=False)
    async def http_off(self, request) -> web.Response:
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
    

    @request_mapping(path="/{id}/action", method="POST", auth_required=auth)
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
              parameter:
                type: object
        responses:
            "204":
                description: successful operation
        """
        actor_id = request.match_info['id']
        data = await request.json()
        print(data)
        await self.controller.call_action(actor_id, data.get("action"), data.get("parameter"))

        return web.Response(status=204)