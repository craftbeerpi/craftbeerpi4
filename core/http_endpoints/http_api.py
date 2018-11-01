import logging
from aiohttp import web
from aiojobs.aiohttp import get_scheduler_from_app

from core.api.decorator import request_mapping
from core.helper.jsondump import json_dumps

class HttpAPI():

    def __init__(self, core):
        self.logger = logging.getLogger(__name__)
        self.logger.info("WOOHOO MY ACTOR")
        self.cbpi = core

    @request_mapping(path="/",  auth_required=False)
    async def http_get_all(self, request):
        return web.json_response(await self.get_all(force_db_update=True), dumps=json_dumps)

    @request_mapping(path="/{id}", auth_required=False)
    async def http_get_one(self, request):
        id = int(request.match_info['id'])
        return web.json_response(await self.get_one(id), dumps=json_dumps)


    @request_mapping(path="/{id}'",  method="POST", auth_required=False)
    async def http_add_one(self, request):
        id = request.match_info['id']
        await self.get_all(force_db_update=True)
        return web.json_response(await self.get_one(id), dumps=json_dumps)

