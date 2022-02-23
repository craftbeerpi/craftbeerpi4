from cbpi.controller.fermentation_controller import FermentationController
from cbpi.api.dataclasses import Fermenter, Step, Props, FermenterStep
from aiohttp import web
from cbpi.api import *
import logging
import json

auth = False

class FermentationHttpEndpoints():

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.controller : FermentationController = cbpi.fermenter
        self.cbpi.register(self, "/fermenter")

    @request_mapping(path="/", auth_required=False)
    async def http_get_all(self, request):
        """
        ---
        description: Show all Fermenters
        tags:
        - Fermenter
        responses:
            "204":
                description: successful operation
        """
        data= self.controller.get_state()
        return web.json_response(data=data)
        

    @request_mapping(path="/", method="POST", auth_required=False)
    async def http_add(self, request):
        """
        ---
        description: add one Fermenter
        tags:
        - Fermenter
        parameters:
        - in: body
          name: body
          description: Create a Fermenter
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
              cooler:
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
              name: "Fermenter 1"
              type: "CustomFermenterLogic"
              sensor: "FermenterSensor"
              heater: "FermenterHeater"
              cooler: "FermenterCooler"
              props: {}
              
        responses:
            "204":
                description: successful operation
        """
        data = await request.json()
        fermenter = Fermenter(id=id, name=data.get("name"), sensor=data.get("sensor"), heater=data.get("heater"), cooler=data.get("cooler"), brewname=data.get("brewname"), target_temp=data.get("target_temp"), props=Props(data.get("props", {})), type=data.get("type"))
        response_data = await self.controller.create(fermenter)
        return web.json_response(data=response_data.to_dict())
        

    @request_mapping(path="/{id}", method="PUT", auth_required=False)
    async def http_update(self, request):
        """
        ---
        description: Update a Fermenter (NOT YET IMPLEMENTED)
        tags:
        - Fermenter
        parameters:
        - name: "id"
          in: "path"
          description: "Fermenter ID"
          required: true
          type: "integer"
          format: "int64"
        - in: body
          name: body
          description: Update a Fermenter
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
        fermenter = Fermenter(id=id, name=data.get("name"), sensor=data.get("sensor"), heater=data.get("heater"), cooler=data.get("cooler"), brewname=data.get("brewname"), target_temp=data.get("target_temp"), props=Props(data.get("props", {})), type=data.get("type"))
        return web.json_response(data=(await self.controller.update(fermenter)).to_dict())
    
    @request_mapping(path="/{id}", method="DELETE", auth_required=False)
    async def http_delete_one(self, request):
        """
        ---
        description: Delete an actor
        tags:
        - Fermenter
        parameters:
        - name: "id"
          in: "path"
          description: "Fermenter ID"
          required: true
          type: "string"
        responses:
            "204":
                description: successful operation
        """
        id = request.match_info['id']
        await self.controller.delete(id)
        return web.Response(status=204)

#    @request_mapping(path="/{id}/on", method="POST", auth_required=False)
#    async def http_on(self, request) -> web.Response:
        """

        ---
        description: Switch actor on
        tags:
        - Fermenter
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
#        id = request.match_info['id']
#        await self.controller.start(id)
#        return web.Response(status=204)

#    @request_mapping(path="/{id}/off", method="POST", auth_required=False)
#    async def http_off(self, request) -> web.Response:
        """

        ---
        description: Switch actor on
        tags:
        - Fermenter

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
#        id = request.match_info['id']
#        await self.controller.off(id)
#        return web.Response(status=204)
    
    @request_mapping(path="/{id}/toggle", method="POST", auth_required=False)
    async def http_toggle(self, request) -> web.Response:
        """

        ---
        description: Switch actor on
        tags:
        - Fermenter

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

#    @request_mapping(path="/{id}/action", method="POST", auth_required=auth)
#    async def http_action(self, request) -> web.Response:
        """

        ---
        description: Toogle an actor on or off
        tags:
        - Fermenter
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
#        actor_id = request.match_info['id']
#        data = await request.json()
#        await self.controller.call_action(actor_id, data.get("name"), data.get("parameter"))

        return web.Response(status=204)
    @request_mapping(path="/{id}/target_temp", method="POST", auth_required=auth)
    async def http_target(self, request) -> web.Response:
        """

        ---
        description: Set Target Temp for Fermenter
        tags:
        - Fermenter
        parameters:
        - name: "id"
          in: "path"
          description: "Fermenter ID"
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

    @request_mapping(path="/{id}/addstep", method="POST", auth_required=False)
    async def http_add_step(self, request):

        """

        ---
        description: Add Fermenterstep
        tags:
        - Fermenter
        parameters:
        - name: "id"
          in: "path"
          description: "Fermenter ID"
          required: true
          type: "integer"
          format: "int64"
        - in: body
          name: body
          description: Create a fermenterstep
          required: true
          schema:
            type: object
        responses:
            "200":
                description: successful operation
        """      

        data = await request.json()
        fermenterid= request.match_info['id']
        newstep = {"name": data.get("name"), "props": data.get("props", {}), "type": data.get("type")}
        response_data = await self.controller.create_step(fermenterid,newstep)
        return web.json_response(data=response_data.to_dict())

    @request_mapping(path="/{fermenterid}/{stepid}", method="PUT", auth_required=False)
    async def http_updatestep(self, request):

        """
        ---
        description: Update FermenterStep
        tags:
        - Fermenter
        parameters:
        - name: "fermenterid"
          in: "path"
          description: "Fermenter ID"
          required: true
          type: "integer"
          format: "int64"
        - name: "stepid"
          in: "path"
          description: "Step ID"
          required: true
          type: "integer"
          format: "int64"
        - in: body
          name: body
          description: Update a Femrenterstep
          required: false
          schema:
            type: object
        responses:
            "200":
                description: successful operation
        """
        
        data = await request.json()
        stepid = request.match_info['stepid']
        fermenterid = request.match_info['fermenterid']
        updatedstep = {"id": stepid, "name": data.get("name"), "props": data.get("props", {}), "type": data.get("type")}
        #step = FermenterStep(stepid, data.get("name"), None, Props(data.get("props", {})), data.get("type"))
        await self.controller.update_step(fermenterid,updatedstep)
        return web.Response(status=200)

    @request_mapping(path="/{fermenterid}/{stepid}", method="DELETE", auth_required=False)
    async def http_deletestep(self, request):
        """
        ---
        description: Delete Fermenterstep
        tags:
        - Fermenter
        parameters:
        - name: "fermenterid"
          in: "path"
          description: "Fermenter ID"
          required: true
          type: "integer"
          format: "int64"
        - name: "stepid"
          in: "path"
          description: "Step ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
        """
        stepid = request.match_info['stepid']
        fermenterid = request.match_info['fermenterid']
        await self.controller.delete_step(fermenterid,stepid)
        return web.Response(status=204)

    @request_mapping(path="/movestep", method="PUT", auth_required=False)
    async def http_movestep(self, request):
        
        """
        ---
        description: Move Fermenterstep
        tags:
        - Fermenter
        parameters:
        - in: body
          name: body
          description: Created an kettle
          required: false
          schema:
            type: object
            properties:
              fermenterid:
                type: string
              stepid:
                type: string
              direction:
                type: "integer"
                format: "int64"
        responses:
            "204":
                description: successful operation
        """
        data = await request.json()
        await self.controller.move_step(data["fermenterid"],data["stepid"], data["direction"])
        return web.Response(status=204)

    @request_mapping(path="/{id}/getsteps", method="GET", auth_required=False)
    async def http_get_steps(self, request):

        """
        ---
        description: Get Fermentersteps for Fermenter
        tags:
        - Fermenter
        parameters:
        - name: "id"
          in: "path"
          description: "Fermenter ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "200":
                description: successful operation
        """      

        fermenterid= request.match_info['id']
        response_data = self.controller.get_step_state(fermenterid)
        return web.json_response(data=response_data)

    @request_mapping(path="/{id}/clearsteps", method="POST", auth_required=False)
    async def http_clear_steps(self, request):

        """
        ---
        description: Clear all steps for Fermenter with fermenterid
        tags:
        - Fermenter
        parameters:
        - name: "id"
          in: "path"
          description: "Fermenter ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "200":
                description: successful operation
        """      

        fermenterid= request.match_info['id']
        await self.controller.clearsteps(fermenterid)
        return web.Response(status=200)

    @request_mapping(path="/{id}/startstep", method="POST", auth_required=False)
    async def http_start_steps(self, request):

        """
        ---
        description: Start steps for Fermenter with fermenterid
        tags:
        - Fermenter
        parameters:
        - name: "id"
          in: "path"
          description: "Fermenter ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "200":
                description: successful operation
        """      

        fermenterid= request.match_info['id']
        await self.controller.start(fermenterid)
        return web.Response(status=200)

    @request_mapping(path="/{id}/stopstep", method="POST", auth_required=False)
    async def http_stop_steps(self, request):

        """
        ---
        description: Stop steps for Fermenter with fermenterid
        tags:
        - Fermenter
        parameters:
        - name: "id"
          in: "path"
          description: "Fermenter ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "200":
                description: successful operation
        """      

        fermenterid= request.match_info['id']
        await self.controller.stop(fermenterid)
        return web.Response(status=200)

    @request_mapping(path="/{id}/nextstep", method="POST", auth_required=False)
    async def http_next_step(self, request):

        """
        ---
        description: Stop steps for Fermenter with fermenterid
        tags:
        - Fermenter
        parameters:
        - name: "id"
          in: "path"
          description: "Fermenter ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "200":
                description: successful operation
        """      

        fermenterid= request.match_info['id']
        await self.controller.next(fermenterid)
        return web.Response(status=200)

    @request_mapping(path="/{id}/nextstep", method="POST", auth_required=False)
    async def http_next_step(self, request):

        """
        ---
        description: Triggers next step for Fermenter with fermenterid
        tags:
        - Fermenter
        parameters:
        - name: "id"
          in: "path"
          description: "Fermenter ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "200":
                description: successful operation
        """      

        fermenterid= request.match_info['id']
        await self.controller.next(fermenterid)
        return web.Response(status=200)

    @request_mapping(path="/{id}/reset", method="POST", auth_required=False)
    async def http_reset(self, request):

        """
        ---
        description: Resets step status for Fermenter with fermenterid
        tags:
        - Fermenter
        parameters:
        - name: "id"
          in: "path"
          description: "Fermenter ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "200":
                description: successful operation
        """      

        fermenterid= request.match_info['id']
        await self.controller.reset(fermenterid)
        return web.Response(status=200)

    @request_mapping(path="/action/{id}", method="POST", auth_required=False)
    async def http_call_action(self, request):
        """
        ---
        description: Call action
        tags:
        - Fermenter
        parameters:
        - name: "id"
          in: "path"
          description: "FermenterStep id"
          required: true
          type: "integer"
          format: "int64"
        - in: body
          name: body
          description: call action for fermenter Step
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