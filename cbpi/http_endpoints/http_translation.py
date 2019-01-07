from aiohttp import web
from aiohttp_auth import auth

from cbpi.api import *


class TranslationHttpEndpoint():

    def __init__(self,cbpi):
        self.cbpi = cbpi
        self.cbpi.register(self, url_prefix="/translation")


    @request_mapping(path="/missing_key", method="POST", auth_required=False)
    async def missing_key(self, request):
        data = await request.json()
        await self.cbpi.translation.add_key(**data)
        return web.Response(status=204)


