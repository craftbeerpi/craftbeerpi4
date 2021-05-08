from aiohttp import web
from cbpi.job.aiohttp import get_scheduler_from_app

from cbpi.api import request_mapping
from cbpi.utils import json_dumps
from cbpi import __version__


class SystemHttpEndpoints:
    def __init__(self, cbpi):
        self.cbpi = cbpi
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
        return web.json_response(
            data=dict(
                actor=self.cbpi.actor.get_state(),
                sensor=self.cbpi.sensor.get_state(),
                kettle=self.cbpi.kettle.get_state(),
                step=self.cbpi.step.get_state(),
                config=self.cbpi.config.get_state(),
                version=__version__,
            ),
            dumps=json_dumps,
        )

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
        log_name = request.match_info["name"]
        self.cbpi.log.delete_log(log_name)

    @request_mapping(path="/logs", method="DELETE", auth_required=False)
    async def delete_all_logs(self, request):
        self.cbpi.log.delete_logs()
        return web.Response(status=204)

    @request_mapping(
        "/events", method="GET", name="get_all_events", auth_required=False
    )
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

    @request_mapping(
        "/restart", method="POST", name="RestartServer", auth_required=False
    )
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

    @request_mapping(
        "/shutdown", method="POST", name="ShutdownSerer", auth_required=False
    )
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
