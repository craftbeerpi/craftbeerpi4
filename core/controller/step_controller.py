import asyncio
from aiohttp import web
from core.api import on_event, request_mapping
from core.controller.crud_controller import CRUDController
from core.database.model import StepModel
from core.http_endpoints.http_api import HttpAPI


class StepController(HttpAPI, CRUDController):

    model = StepModel

    def __init__(self, cbpi):
        super(StepController, self).__init__(cbpi)

        self.cbpi = cbpi
        self.current_task = None
        self.types = {}

        self.current_step = None
        self.cbpi.register(self, "/step")

    async def init(self):
        #self.start()

        await super(StepController, self).init()
        pass

    @request_mapping(path="/action", auth_required=False)
    async def http_action(self, request):
        self.cbpi.bus.fire("step/action", action="test")
        return web.Response(text="OK")


    @request_mapping(path="/start", auth_required=False)
    async def http_start(self, request):
        self.cbpi.bus.fire("step/start")
        return web.Response(text="OK")

    @request_mapping(path="/reset", auth_required=False)
    async def http_reset(self, request):
        self.cbpi.bus.fire("step/reset")
        return web.Response(text="OK")

    @request_mapping(path="/next", auth_required=False)
    async def http_reset(self, request):
        self.cbpi.bus.fire("step/next")
        return web.Response(text="OK")

    @on_event("step/action")
    def handle_action(self, topic, action, **kwargs):
        print("process action")
        if self.current_step is not None:
            self.current_step.__getattribute__(action)()
            pass

    @on_event("step/next")
    def handle_next(self, **kwargs):
        print("process action")
        if self.current_step is not None:
            self.current_step.next()
            pass



    @on_event("step/start")
    def handle_start(self, topic, **kwargs):
        self.start()

    @on_event("step/reset")
    def handle_reset(self, topic, **kwargs):
        if self.current_step is not None:
            self.current_task.cancel()
            self.current_step.reset()

            self.steps[self.current_step.id]["state"] = None
            self.current_step = None
            self.current_task = None
            self.start()

    @on_event("step/stop")
    def handle_stop(self, topic, **kwargs):
        if self.current_step is not None:
            self.current_step.stop()

        for key, step in self.cache.items():
            step.state = None

        self.current_step = None

    @on_event("step/+/done")
    def handle(self, topic, **kwargs):
        self.start()

    def _step_done(self, task):

        if task.cancelled() == False:
            self.cache[self.current_step.id].state = "D"
            step_id = self.current_step.id
            self.current_step = None
            self.cbpi.bus.fire("step/%s/done" % step_id)

    def get_manged_fields_as_array(self, type_cfg):
        print("tYPE", type_cfg)
        result = []
        for f in type_cfg.get("properties"):
            result.append(f.get("name"))

        return result

    def start(self):

        if self.current_step is None:
            loop = asyncio.get_event_loop()
            open_step = False
            for key, step in self.cache.items():
                if step.state is None:
                    step_type = self.types["CustomStep"]
                    print("----------")
                    print(step_type)
                    print("----------")
                    config = dict(cbpi = self.cbpi, id=key, name=step.name, managed_fields=self.get_manged_fields_as_array(step_type))
                    self.current_step = step_type["class"](**config)
                    self.current_task = loop.create_task(self.current_step.run())
                    self.current_task.add_done_callback(self._step_done)
                    open_step = True
                    break
            if open_step == False:
                self.cbpi.bus.fire("step/berwing/finished")
    async def stop(self):
        pass
