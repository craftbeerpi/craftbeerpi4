import logging
import time

from cbpi.api import *
from cbpi.controller.crud_controller import CRUDController
from cbpi.database.model import StepModel


class StepController(CRUDController):



    def __init__(self, cbpi):
        self.model = StepModel

        self.caching = True
        self.is_stopping = False
        self.cbpi = cbpi
        self.current_task = None
        self.is_next = False
        self.types = {}
        self.current_step = None
        self.current_job = None
        self.cbpi.register(self)
        self.logger = logging.getLogger(__name__)
        self.starttime = None

    def is_running(self):
        if self.current_step is not None:
            return True
        else:
            return False



    def _get_manged_fields_as_array(self, type_cfg):

        result = []

        for f in type_cfg.get("properties"):

            result.append(f.get("name"))

        return result

    async def init(self):

        # load all steps into cache
        self.cache = await self.model.get_all()


        for key, value in self.cache.items():

            # get step type as string
            step_type = self.types.get(value.type)

            # if step has state
            if value.stepstate is not None:
                cfg = value.stepstate.copy()
            else:
                cfg = {}

            # set managed fields
            cfg.update(dict(cbpi=self.cbpi, id=value.id, managed_fields=self._get_manged_fields_as_array(step_type)))

            if value.config is not None:
                # set config values
                cfg.update(**value.config)
            # create step instance
            value.instance = step_type["class"](**cfg)

    async def get_all(self, force_db_update: bool = True):
        return self.cache

    def find_next_step(self):
        # filter
        inactive_steps = {k: v for k, v in self.cache.items() if v.state == 'I'}
        if len(inactive_steps) == 0:
            return None
        return min(inactive_steps, key=lambda x: inactive_steps[x].order)

    @on_event("step/start")
    async def start(self, **kwargs):

        if self.is_running() is False:
            next_step_id = self.find_next_step()
            if next_step_id:
                next_step = self.cache[next_step_id]
                next_step.state = 'A'
                next_step.stepstate = next_step.config
                next_step.start = int(time.time())
                await self.model.update(**next_step.__dict__)
                self.current_step = next_step
                # start the step job
                self.current_job = await self.cbpi.job.start_job(self.current_step.instance.run(), next_step.name, "step")
                await self.cbpi.bus.fire("step/%s/started" % self.current_step.id, step=next_step)
            else:
                await self.cbpi.bus.fire("step/brewing/finished")
        else:
            self.logger.error("Process Already Running")

    async def next(self, **kwargs):

        if self.current_step is not None:

            self.is_next = True
            self.current_step.instance.stop()

    @on_event("job/step/done")
    async def step_done(self, **kwargs):

        if self.cbpi.shutdown:
            return
        if self.is_stopping:
            self.is_stopping = False
            return

        if self.current_step is not None:

            self.current_step.state = "D"
            await self.model.update_state(self.current_step.id, "D", int(time.time()))
            await self.cbpi.bus.fire("step/%s/done" % self.current_step.id, step=self.current_step)
            self.current_step = None

        # start the next step
        await self.start()

    @on_event("step/stop")
    async def stop_all(self, **kwargs):
        # RESET DB
        await self.model.reset_all_steps()
        # RELOAD all Steps from DB into cache and initialize Instances
        await self.init()
        await self.cbpi.bus.fire("step/brewing/stopped")

    @on_event("step/clear")
    async def clear_all(self, **kwargs):
        await self.model.delete_all()
        self.cbpi.notify(key="Steps Cleared", message="Steps cleared successfully", type="success")

    async def _pre_add_callback(self, data):

        order = await self.model.get_max_order()
        data["order"] = 1 if order is None else order + 1
        data["state"] = "I"
        data["stepstate"] = {}
        return await super()._pre_add_callback(data)

    async def init_step(self, value: StepModel):
        step_type = self.types.get(value.type)

        # if step has state
        if value.stepstate is not None:
            cfg = value.stepstate.copy()
        else:
            cfg = {}

        # set managed fields
        cfg.update(dict(cbpi=self.cbpi, id=value.id, managed_fields=self._get_manged_fields_as_array(step_type)))
        # set config values
        cfg.update(**value.config)
        # create step instance
        value.instance = step_type["class"](**cfg)
        return value

    async def _post_add_callback(self, m: StepModel) -> None:
        self.cache[m.id] = await self.init_step(m)

    async def _post_update_callback(self, m: StepModel) -> None:
        '''
        :param m: step model
        :return: None
        '''
        self.cache[m.id] = await self.init_step(m)

    @on_event("step/sort")
    async def sort(self, topic: 'str', data: 'dict', **kwargs):

        # update order in cache
        for id, order in data.items():
            self.cache[int(id)].order = order

        # update oder in database
        await self.model.sort(data)

    async def get_state(self):
        return dict(items=await self.get_all(),types=self.types,is_running=self.is_running(),current_step=self.current_step)

    @on_event(topic="step/action")
    async def call_action(self, name, parameter, **kwargs) -> None:
        print(name, parameter)
        if self.current_step is not None:

            self.current_step.instance.__getattribute__(name)(**parameter)
