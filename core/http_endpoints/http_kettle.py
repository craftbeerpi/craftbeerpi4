from aiohttp import web
from cbpi_api import request_mapping


from http_endpoints.http_curd_endpoints import HttpCrudEndpoints
auth = False


class KettleHttpEndpoints(HttpCrudEndpoints):

    def __init__(self, cbpi):
        super().__init__(cbpi)
        self.controller = cbpi.kettle
        self.cbpi.register(self, "/kettle")

    @request_mapping(path="/{id:\d+}/automatic", auth_required=False)
    async def http_automatic(self, request):
        await self.controller.toggle_automtic(int(request.match_info['id']))
        return web.Response(status=204)

    @request_mapping(path="/{id:\d+}/heater/on", auth_required=False)
    async def http_heater_on(self, request):
        await self.controller.heater_on(int(request.match_info['id']))
        return web.Response(status=204)

    @request_mapping(path="/{id:\d+}/heater/off", auth_required=False)
    async def http_heater_off(self, request):
        await self.controller.heater_off(int(request.match_info['id']))
        return web.Response(status=204)

    @request_mapping(path="/{id:\d+}/agitator/on", auth_required=False)
    async def http_agitator_on(self, request):
        await self.controller.agitator_on(int(request.match_info['id']))
        return web.Response(status=204)

    @request_mapping(path="/{id:\d+}/agitator/off", auth_required=False)
    async def http_agitator_off(self, request):
        await self.controller.agitator_off(int(request.match_info['id']))
        return web.Response(status=204)

    @request_mapping(path="/{id:\d+}/targettemp", auth_required=False)
    async def http_taget_temp(self, request):
        kettle_id = int(request.match_info['id'])
        temp = await self.controller.get_traget_temp(kettle_id)
        return web.json_response(data=dict(target_temp=temp, kettle_id=kettle_id))

    @request_mapping(path="/{id:\d+}/temp", auth_required=False)
    async def http_temp(self, request):
        kettle_id = int(request.match_info['id'])
        temp = await self.controller.get_temp(kettle_id)
        return web.json_response(data=dict(temp=temp, kettle_id=kettle_id))

