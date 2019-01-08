from aiohttp import web
from aiohttp_auth import auth

from cbpi.api import *


class TranslationHttpEndpoint():

    def __init__(self,cbpi):
        self.cbpi = cbpi
        self.cbpi.register(self, url_prefix="/translation")


    @request_mapping(path="/missing_key", method="POST", auth_required=False)
    async def missing_key(self, request):
        """
        ---
        description: Add missing translation key
        tags:
        - Translation
        parameters:
        - in: body
          name: body
          description: missing key data
          required: true
          schema:
            type: object
            properties:
              locale:
                type: string
              key:
                type: string
        responses:
            "204":
                description: successful operation
        """

        data = await request.json()
        await self.cbpi.translation.add_key(**data)
        return web.Response(status=204)

    @request_mapping(path="/", auth_required=False)
    async def http_get_all(self, request):
        """
        ---
        description: Get all translations
        tags:
        - Translation
        responses:
            "200":
                description: successful operation
        """

        return web.json_response(data=self.cbpi.translation.get_all())
