from cbpi.controller.upload_controller import UploadController
from cbpi.api.dataclasses import Props, Step
from aiohttp import web
from cbpi.api import *
import logging

class UploadHttpEndpoints():

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.controller : UploadController = cbpi.upload
        self.cbpi.register(self, "/upload")


    @request_mapping(path='/', method="POST", auth_required=False)
    async def FileUpload(self, request):
        data = await request.post()
        await self.controller.FileUpload(data)
        return web.Response(status=200)




    @request_mapping(path='/kbh', method="GET", auth_required=False)
    async def get_kbh_list(self, request):
        """

        ---
        description: Get Recipe list from Kleiner Brauhelfer 
        tags:
        - Upload
        responses:
            "200":
                description: successful operation
        """

        kbh_list = await self.controller.get_kbh_recipes()
        return web.json_response(kbh_list)

    @request_mapping(path='/kbh', method="POST", auth_required=False)
    async def create_kbh_recipe(self, request):
        """

        ---
        description: Create Recipe from KBH database with selected ID
        tags:
        - Upload
        parameters:
        - name: "id"
          in: "body"
          description: "Recipe ID: {'id': ID}"
          required: true
          type: "string"
        responses:
            "200":
                description: successful operation
        """

        kbh_id = await request.json()
        await self.controller.kbh_recipe_creation(kbh_id['id'])
        return web.Response(status=200)

    @request_mapping(path='/xml', method="GET", auth_required=False)
    async def get_xml_list(self, request):
        """

        ---
        description: Get recipe list from xml file
        tags:
        - Upload
        responses:
            "200":
                description: successful operation
        """

        xml_list = await self.controller.get_xml_recipes()

        return web.json_response(xml_list)

    @request_mapping(path='/xml', method="POST", auth_required=False)
    async def create_xml_recipe(self, request):
        """

        ---
        description: Create recipe from xml file with selected id
        tags:
        - Upload
        parameters:
        - name: "id"
          in: "body"
          description: "Recipe ID: {'id': ID}"
          required: true
          type: "string"

        responses:
            "200":
                description: successful operation
        """

        xml_id = await request.json()
        await self.controller.xml_recipe_creation(xml_id['id'])
        return web.Response(status=200)

    @request_mapping(path="/getpath", auth_required=False)
    async def http_getpath(self, request):
        
        """

        ---
        description: get path for recipe creation
        tags:
        - Upload
        responses:
            "200":
                description: successful operation
        """
        return  web.json_response(data=self.controller.get_creation_path())

