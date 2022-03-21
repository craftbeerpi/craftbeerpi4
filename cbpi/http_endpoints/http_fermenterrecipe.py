from cbpi.controller.fermenter_recipe_controller import FermenterRecipeController
from cbpi.api.dataclasses import Props, Step
from aiohttp import web
from cbpi.api import *
import logging

class FermenterRecipeHttpEndpoints():

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.controller : FermenterRecipeController = cbpi.fermenterrecipe
        self.cbpi.register(self, "/fermenterrecipe")

    @request_mapping(path="/", method="GET", auth_required=False)
    async def http_get_all(self, request):
        """
        ---
        description: Get all recipes
        tags:
        - FermenterRecipe
        responses:
            "200":
                description: successful operation
        """
        return web.json_response(await self.controller.get_recipes())

    @request_mapping(path="/{name}", method="GET", auth_required=False)
    async def get_by_name(self, request):
        """
        ---
        description: Get all recipes
        tags:
        - FermenterRecipe
        parameters:
        - name: "name"
          in: "path"
          description: "Recipe Name"
          required: true
          type: "string"
        responses:
            "200":
                description: successful operation
        """
        name = request.match_info['name']
        return web.json_response(await self.controller.get_by_name(name))

    @request_mapping(path="/create", method="POST", auth_required=False)
    async def http_create(self, request):

        """
        ---
        description: Add Recipe
        tags:
        - FermenterRecipe
        
        responses:
            "200":
                description: successful operation
        """
        data = await request.json()
        print(data)
        return web.json_response(dict(id=await self.controller.create(data.get("name"))))
       
    
    @request_mapping(path="/{name}", method="PUT", auth_required=False)
    async def http_save(self, request):

        """
        ---
        description: Save Recipe
        tags:
        - FermenterRecipe
        parameters:
        - name: "id"
          in: "path"
          description: "Recipe Id"
          required: true
          type: "string"
        - in: body
          name: body
          description: Recipe Data
          required: false
          schema:
            type: object
            
        responses:
            "200":
                description: successful operation
        """
        data = await request.json()
        name = request.match_info['name']
        await self.controller.save(name, data)
        print(data)
        return web.Response(status=204)
    
    @request_mapping(path="/{name}", method="DELETE", auth_required=False)
    async def http_remove(self, request):

        """
        ---
        description: Delete
        tags:
        - FermenterRecipe
        parameters:
        - name: "id"
          in: "path"
          description: "Recipe Id"
          required: true
          type: "string"
        
            
        responses:
            "200":
                description: successful operation
        """
        name = request.match_info['name']
        await self.controller.remove(name)
        return web.Response(status=204)

    @request_mapping(path="/{recipeid}/{fermenterid}/{name}/brew", method="POST", auth_required=False)
    async def http_brew(self, request):

        """
        ---
        description: Send Recipe to Fermenter
        tags:
        - FermenterRecipe
        parameters:
        - name: "name"
          in: "path"
          description: "Recipe Id"
          required: true
          type: "string"
        
            
        responses:
            "200":
                description: successful operation
        """
        recipeid = request.match_info['recipeid']
        name = request.match_info['name']
        fermenterid = request.match_info['fermenterid']
        await self.controller.brew(recipeid,fermenterid,name)
        return web.Response(status=204)
    
    @request_mapping(path="/{id}/clone", method="POST", auth_required=False)
    async def http_clone(self, request):

        """
        ---
        description: Brew
        tags:
        - FermenterRecipe
        parameters:
        - name: "id"
          in: "path"
          description: "Recipe Id"
          required: true
          type: "string"
        - in: body
          name: body
          description: Recipe Data
          required: false
          schema:
            type: object
        responses:
            "200":
                description: successful operation
        """
        id = request.match_info['id']
        data = await request.json()      
        return web.json_response(dict(id=await self.controller.clone(id, data.get("name"))))
        
