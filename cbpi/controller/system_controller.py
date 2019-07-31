import datetime
import re

import aiohttp
from aiohttp import web
import os
from aiojobs.aiohttp import get_scheduler_from_app

from cbpi.api import *

from cbpi.utils import json_dumps


class SystemController():

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.service = cbpi.actor

        self.cbpi.register(self, "/system")
        self.cbpi.app.on_startup.append(self.check_for_update)


    async def check_for_update(self, app):
        timeout = aiohttp.ClientTimeout(total=1)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.post('http://localhost:2202/check', json=dict(version=app["cbpi"].version)) as resp:
                if (resp.status == 200):
                    data = await resp.json()
                    print(data)



    @request_mapping("/", method="GET", auth_required=False)
    async def state(self, request):
        """
        ---
        description: Get complete system state
        tags:
        - System
        responses:
            "200":
                description: successful operation
        """
        return web.json_response(data=dict(
            actor=self.cbpi.actor.get_state(),
            sensor=self.cbpi.sensor.get_state(),
            kettle=self.cbpi.kettle.get_state(),
            step=await self.cbpi.step.get_state(),
            dashboard=self.cbpi.dashboard.get_state(),
            translations=self.cbpi.translation.get_all(),
            config=self.cbpi.config.get_state())
            , dumps=json_dumps)

    @request_mapping("/restart", method="POST", name="RestartServer", auth_required=False)
    def restart(self, request):
        """
        ---
        description: Restart System - Not implemented
        tags:
        - System
        responses:
            "200":
                description: successful operation
        """
        return web.Response(text="NOT IMPLEMENTED")

    @request_mapping("/shutdown", method="POST", name="ShutdownSerer", auth_required=False)
    def shutdown(self, request):
        """
        ---
        description: Shutdown System - Not implemented
        tags:
        - System
        responses:
            "200":
                description: successful operation
        """
        return web.Response(text="NOT IMPLEMENTED")

    @request_mapping("/jobs", method="GET", name="get_jobs", auth_required=False)
    def get_all_jobs(self, request):
        """
        ---
        description: Get all running Jobs
        tags:
        - System
        responses:
            "200":
                description: successful operation
        """
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
        """
        ---
        description: Get list of all registered events
        tags:
        - System
        responses:
            "200":
                description: successful operation
        """
        return web.json_response(data=self.cbpi.bus.dump())

    @request_mapping(path="/logs", auth_required=False)
    async def http_get_log(self, request):
        result = []
        file_pattern = re.compile("^(\w+.).log(.?\d*)")
        for filename in sorted(os.listdir("./logs"), reverse=True):#
            if file_pattern.match(filename):
                result.append(filename)

        return web.json_response(result)

    @request_mapping(path="/logs/{name}", method="DELETE", auth_required=False)
    async def http_delete_log(self, request):
        log_name = request.match_info['name']
        file_patter = re.compile("^(\w+.).log(.?\d*)")
        file_sensor_log = re.compile("^sensor_(\d).log(.?\d*)")

        if file_patter.match(log_name):

            pass



    @request_mapping(path="/logs", method="DELETE", auth_required=False)
    async def http_delete_logs(self, request):

        sensor_log_pattern = re.compile("sensor_([\d]).log$")
        sensor_log_pattern2 = re.compile("sensor_([\d]).log.[\d]*$")

        app_log_pattern = re.compile("app.log$")

        for filename in sorted(os.listdir("./logs"), reverse=True):#
            if app_log_pattern.match(filename):
                with open(os.path.join("./logs/%s" % filename), 'w'):
                    pass
                continue


        for filename in sorted(os.listdir("./logs/sensors"), reverse=True):

            if sensor_log_pattern.match(filename):
                with open(os.path.join("./logs/sensors/%s" % filename), 'w'):
                    pass
                continue
            elif sensor_log_pattern2.match(filename):
                os.remove(os.path.join("./logs/sensors/%s" % filename))

        return web.Response(status=204)