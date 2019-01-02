import datetime
from aiohttp import web
from aiojobs.aiohttp import get_scheduler_from_app

from cbpi_api import *


class SystemController():

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.service = cbpi.actor
        self.cbpi.register(self, "/system")

    @request_mapping("/restart", method="POST", name="RestartServer", auth_required=False)
    def restart(self, request):
        # TODO implement restart
        return web.Response(text="NOT IMPLEMENTED")

    @request_mapping("/shutdown", method="POST", name="ShutdownSerer", auth_required=False)
    def restart(self, request):
        # TODO implement restart
        return web.Response(text="NOT IMPLEMENTED")

    @request_mapping("/jobs", method="GET", name="get_jobs", auth_required=False)
    def get_all_jobs(self, request):
        scheduler = get_scheduler_from_app(self.cbpi.app)
        result = []
        for j in scheduler:
            try:
                result.append(dict(name=j.name, type=j.type, time=j.start_time))
            except:
                pass
        return web.json_response(data=result)

    @request_mapping("/events", method="GET", name="get_all_events", auth_required=False)
    def get_all_events(self, request):
        return web.json_response(data=self.cbpi.bus.dump())