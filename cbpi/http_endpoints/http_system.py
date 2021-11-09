from aiohttp import web
from aiohttp import streamer
from cbpi.job.aiohttp import get_scheduler_from_app
import logging
from cbpi.api import request_mapping
from cbpi.utils import json_dumps
from cbpi import __version__
import pathlib
import os
import json

class SystemHttpEndpoints:

    def __init__(self,cbpi):
        self.cbpi = cbpi
        self.controller : SystemController = cbpi.system
        self.cbpi.register(self, url_prefix="/system")

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
            step=self.cbpi.step.get_state(),
            config=self.cbpi.config.get_state(),
            version=__version__)
            , dumps=json_dumps)

    @request_mapping(path="/logs", auth_required=False)
    async def http_get_log(self, request):
        result = []
        file_pattern = re.compile("^(\w+.).log(.?\d*)")
        for filename in sorted(os.listdir("./logs"), reverse=True):  #
            if file_pattern.match(filename):
                result.append(filename)
        return web.json_response(result)

    @request_mapping(path="/logs/{name}", method="DELETE", auth_required=False)
    async def delete_log(self, request):
        log_name = request.match_info['name']
        self.cbpi.log.delete_log(log_name)

    @request_mapping(path="/logs", method="DELETE", auth_required=False)
    async def delete_all_logs(self, request):
        self.cbpi.log.delete_logs()
        return web.Response(status=204)

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

    @request_mapping("/restart", method="POST", name="RestartServer", auth_required=False)
    async def restart(self, request):
        """
        ---
        description: Restart System
        tags:
        - System
        responses:
            "200":
                description: successful operation
        """
        await self.controller.restart()
        return web.Response(text="RESTART")

    @request_mapping("/shutdown", method="POST", name="ShutdownSerer", auth_required=False)
    async def shutdown(self, request):
        """
        ---
        description: Shutdown System
        tags:
        - System
        responses:
            "200":
                description: successful operation
        """
        await self.controller.shutdown()
        return web.Response(text="SHUTDOWN")

    @request_mapping("/backup", method="GET", name="BackupConfig", auth_required=False)
    async def backup(self, request):
        """
        ---
        description: Zip and download Config Folder 
        tags:
        - System
        responses:
            "200":
                description: successful operation
                content:  # Response body
                application/zip:  # Media type
        """
        await self.controller.backupConfig()
        filename = "cbpi4_config.zip"
        file_name = pathlib.Path(os.path.join(".", filename))

        response = web.StreamResponse(
            status=200,
            reason='OK',
            headers={'Content-Type': 'application/zip'},
        )
        await response.prepare(request)
        with open(file_name, 'rb') as file:
            for line in file.readlines():
                await response.write(line)

        await response.write_eof()
        return response

    @request_mapping("/restore", method="POST", name="RestoreConfig", auth_required=False)
    async def restore(self, request):
        """
        ---
        description: Restore Config
        tags:
        - System
        responses:
            "200":
                description: successful operation
        """
        logging.info("Restore Config")
        data = await request.post()
        logging.info("Data received")
        await self.controller.restoreConfig(data)
        return web.Response(status=200)

    @request_mapping("/systeminfo", method="GET", name="SystemInfo", auth_required=False)
    async def systeminfo(self, request):
        """
        ---
        description: System Information
        tags:
        - System
        responses:
            "200":
                description: successful operation
        """
        systeminfo = await self.controller.systeminfo()
        return web.json_response(data=systeminfo)

    @request_mapping("/uploadsvg", method="POST", name="UploadSVG", auth_required=False)
    async def uploadSVG(self, request):
        """
        ---
        description: Upload SVG file to widgets folder 
        tags:
        - System
        responses:
            "200":
                description: successful operation
        """
        logging.info("Upload SVG file")
        data = await request.post()
        logging.info("Data received")
        await self.controller.uploadSVG(data)
        return web.Response(status=200)