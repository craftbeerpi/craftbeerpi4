#from cbpi.controller.recipe_controller import RecipeController
from cbpi.api.dataclasses import Props, Step
from aiohttp import web
from cbpi.api import *

class UploadHttpEndpoints():

    def __init__(self, cbpi):
        self.cbpi = cbpi
#        self.controller : RecipeController = cbpi.recipe
        self.cbpi.register(self, "/fileupload")


    @request_mapping(path='/', method="POST", auth_required=False)
    async def RecipeUpload(self, request):
        """

        ---
        description: Upload XML file or database from KBH V2 
        tags:
        - FileUpload
        requestBody:
            content:
                multipart/form-data:
                    schema:
                      type: object
                      properties:
                        orderId:
                          type: integer
                        userId:
                          type: integer
                        fileName:
                          type: string
                          format: binary
        responses:
            "200":
                description: successful operation
        """

        data = await request.post()
        fileData = data['File']
        logging.info(fileData)


    @request_mapping(path='/kbh', method="GET", auth_required=False)
    async def get_kbh_list(self, request):
        """

        ---
        description: Get Recipe list from Kleiner Brauhelfer 
        tags:
        - FileUpload
        responses:
            "200":
                description: successful operation
        """

        kbh_list = await get_kbh_recipes()
        return web.json_response(kbh_list)

    @request_mapping(path='/kbh', method="POST", auth_required=False)
    async def create_kbh_recipe(self, request):
        """

        ---
        description: Create Recipe from KBH database with selected ID
        tags:
        - FileUpload
        responses:
            "200":
                description: successful operation
        """

        kbh_id = await request.json()
        await self.kbh_recipe_creation(kbh_id['id'])
        return web.Response(status=200)

    @request_mapping(path='/xml', method="GET", auth_required=False)
    async def get_xml_list(self, request):
        """

        ---
        description: Get recipe list from xml file
        tags:
        - FileUpload
        responses:
            "200":
                description: successful operation
        """

        xml_list = await get_xml_recipes()
        return web.json_response(xml_list)

    @request_mapping(path='/xml', method="POST", auth_required=False)
    async def create_xml_recipe(self, request):
        """

        ---
        description: Create recipe from xml file with selected id
        tags:
        - FileUpload
        responses:
            "200":
                description: successful operation
        """

        xml_id = await request.json()
        await self.xml_recipe_creation(xml_id['id'])
        return web.Response(status=200)

    @request_mapping(path="/getpath", auth_required=False)
    async def http_getpath(self, request):
        
        """

        ---
        description: get path for recipe creation
        tags:
        - FileUpload
        responses:
            "200":
                description: successful operation
        """
        return  web.json_response(data=self.get_creation_path())

