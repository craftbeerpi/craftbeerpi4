import asyncio
from aiohttp import web
from core.api import on_event, request_mapping

class StepController():

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.types = {}
        self.steps = {
            1: dict(name="S1", config=dict(time=1), type="CustomStep", state=None),
            2: dict(name="S2", config=dict(time=1), type="CustomStep", state=None),
            3: dict(name="S3", config=dict(time=1), type="CustomStep", state=None)
        }
        self.current_step = None
        self.cbpi.register(self, "/step")

    async def init(self):
        #self.start()
        pass

    @request_mapping(path="/start", auth_required=False)
    async def http_start(self, request):
        self.cbpi.bus.fire("step/start")
        return web.Response(text="OK")

    @request_mapping(path="/reset", auth_required=False)
    async def http_reset(self, request):
        self.cbpi.bus.fire("step/reset")
        return web.Response(text="OK")

    @on_event("step/start")
    def handle_start(self, topic, **kwargs):
        self.start()

    @on_event("step/reset")
    def handle_rest(self, topic, **kwargs):
        for key, step in self.steps.items():
            step["state"] = None

        self.current_step = Nonecd

    @on_event("step/+/done")
    def handle(self, topic, **kwargs):
        self.start()

    def _step_done(self, task):
        self.steps[self.current_step.id]["state"] = "D"
        step_id = self.current_step.id
        self.current_step = None
        self.cbpi.bus.fire("step/%s/done" % step_id)

    def start(self):

        if self.current_step is None:
            loop = asyncio.get_event_loop()
            open_step = False
            for key, step in self.steps.items():
                if step["state"] is None:
                    type = self.types.get(step["type"])
                    self.current_step = type["class"](key, self.cbpi)
                    task = loop.create_task(self.current_step.run())
                    task.add_done_callback(self._step_done)
                    open_step = True
                    break
            if open_step == False:
                self.cbpi.bus.fire("step/berwing/finished")
    async def stop(self):
        pass
