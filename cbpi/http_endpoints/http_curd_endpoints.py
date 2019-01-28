import logging

from aiohttp import web
from cbpi.api import *

from cbpi.utils.utils import json_dumps


class HttpCrudEndpoints():

    def __init__(self, cbpi):
        self.logger = logging.getLogger(__name__)
        self.cbpi = cbpi
        

    @request_mapping(path="/types", auth_required=False)
    async def get_types(self, request):
        if self.controller.types is not None:
            return web.json_response(data=self.controller.types, dumps=json_dumps)
        else:
            return web.Response(status=404, text="Types not supported by endpoint")

    @request_mapping(path="/", auth_required=False)
    async def http_get_all(self, request):
        return web.json_response(await self.controller.get_all(force_db_update=True), dumps=json_dumps)

    @request_mapping(path="/{id:\d+}", auth_required=False)
    async def http_get_one(self, request):
        id = int(request.match_info['id'])
        return web.json_response(await self.controller.get_one(id), dumps=json_dumps)

    @request_mapping(path="/", method="POST", auth_required=False)
    async def http_add(self, request):
        data = await request.json()
        obj = await self.controller.add(**data)
        return web.json_response(obj, dumps=json_dumps)

    @request_mapping(path="/{id}", method="PUT", auth_required=False)
    async def http_update(self, request):
        id = int(request.match_info['id'])
        data = await request.json()
        obj = await self.controller.update(id, data)
        return web.json_response(obj, dumps=json_dumps)

    @request_mapping(path="/{id}", method="DELETE", auth_required=False)
    async def http_delete_one(self, request):
        id = request.match_info['id']
        await self.controller.delete(int(id))
        return web.Response(status=204)
