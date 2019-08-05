from aiohttp import web
from cbpi.utils.utils import json_dumps
from cbpi.api import request_mapping

class LogHttpEndpoints:

    def __init__(self,cbpi):
        self.cbpi = cbpi
        self.cbpi.register(self, url_prefix="/log")

    @request_mapping(path="/{name}/zip", method="POST", auth_required=False)
    async def create_zip_names(self, request):
        log_name = request.match_info['name']
        data = self.cbpi.log.zip_log_data(log_name)
        print(data)
        return web.json_response(dict(filename=data), dumps=json_dumps)

    @request_mapping(path="/{name}/zip", method="DELETE", auth_required=False)
    async def clear_zip_names(self, request):
        log_name = request.match_info['name']
        self.cbpi.log.clear_zip(log_name)
        return web.Response(status=204)

    @request_mapping(path="/zip/download/{name}", method="GET", auth_required=False)
    async def download_zip(self, request):
        response = web.StreamResponse(
            status=200,
            reason='OK',
            headers={'Content-Type': 'application/zip'},
        )
        await response.prepare(request)
        log_name = request.match_info['name']
        with open('./logs/%s.zip' % log_name, 'rb') as file:
            for line in file.readlines():
                await response.write(line)

        await response.write_eof()
        return response

    @request_mapping(path="/{name}/zip", method="GET", auth_required=False)
    async def get_zip_names(self, request):
        log_name = request.match_info['name']
        data = self.cbpi.log.get_all_zip_file_names(log_name)
        return web.json_response(data, dumps=json_dumps)

    @request_mapping(path="/{name}/files", method="GET", auth_required=False)
    async def get_file_names(self, request):
        log_name = request.match_info['name']
        print(log_name)
        data = self.cbpi.log.get_logfile_names(log_name)
        return web.json_response(data, dumps=json_dumps)

    @request_mapping(path="/{name}", method="GET", auth_required=False)
    async def delete_log(self, request):
        log_name = request.match_info['name']
        data = await self.cbpi.log.get_data(log_name)
        return web.json_response(data, dumps=json_dumps)

    @request_mapping(path="/{name}", method="DELETE", auth_required=False)
    async def delete_all_logs(self, request):
        log_name = request.match_info['name']
        await self.cbpi.log.clear_logs(log_name)
        return web.Response(status=204)