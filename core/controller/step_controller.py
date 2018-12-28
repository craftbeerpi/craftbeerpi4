import asyncio

import time
from aiohttp import web
from cbpi_api import *
from core.controller.crud_controller import CRUDController
from core.database.model import StepModel
from core.http_endpoints.http_api import HttpAPI
from core.job.aiohttp import get_scheduler_from_app


class StepController(HttpAPI, CRUDController):
    '''
    The Step Controller. This controller is responsible to start and stop the brewing steps.
    
    '''


    model = StepModel

    def __init__(self, cbpi):
        super(StepController, self).__init__(cbpi)

        self.cbpi = cbpi
        self.current_task = None
        self.types = {}

        self.current_step = None
        self.cbpi.register(self, "/step")



    async def init(self):
        '''
        Initializer of the the Step Controller. 
        :return: 
        '''
        await super(StepController, self).init()

        await self.init_after_startup()

    async def init_after_startup(self):
        step = await self.model.get_by_state('A')
        # We have an active step


        if step is not None:

            # get the type

            step_type = self.types.get(step.type)

            if step_type is None:
                # step type not found. cant restart step

                return

            if step.stepstate is not None:
                cfg = step.stepstate.copy()
            else:
                cfg = {}
            cfg.update(dict(cbpi=self.cbpi, id=step.id, managed_fields=self._get_manged_fields_as_array(step_type)))

            self.current_step = step_type["class"](**cfg)
            self.current_job = await self.cbpi.start_job(self.current_step.run(), step.name, "step")

    @request_mapping(path="/action", auth_required=False)
    async def http_action(self, request):

        '''
        HTTP Endpoint to call an action on the current step. 
        
        :param request: web requset
        :return: web.Response(text="OK"
        '''
        await self.cbpi.bus.fire("step/action", action="test")
        return web.Response(text="OK")


    @request_mapping(path="/start", auth_required=False)
    async def http_start(self, request):

        '''
        HTTP Endpoint to start the brewing process.
        
        :param request: 
        :return: 
        '''

        await self.cbpi.bus.fire("step/start")
        return web.Response(text="OK")

    @request_mapping(path="/reset", auth_required=False)
    async def http_reset(self, request):
        '''
        HTTP Endpoint to call reset on the current step.
        
        :param request: 
        :return: 
        '''
        await self.cbpi.bus.fire("step/reset")
        return web.Response(text="OK")

    @request_mapping(path="/next", auth_required=False)
    async def http_next(self, request):

        '''
        HTTP Endpoint to start the next step. The current step will be stopped
        
        :param request: 
        :return: 
        '''
        await self.cbpi.bus.fire("step/next")
        return web.Response(text="OK")

    @on_event("step/action")
    async def handle_action(self, action, **kwargs):

        '''
        Event Handler for "step/action".
        It invokes the provided method name on the current step
        
        
        :param action: the method name which will be invoked
        :param kwargs: 
        :return: None
        '''
        if self.current_step is not None:
            self.current_step.__getattribute__(action)()


    @on_event("step/next")
    async def handle_next(self, **kwargs):
        '''
        Event Handler for "step/next".
        It start the next step
        
        :param kwargs: 
        :return: None
        '''
        if self.current_step is not None:

            self.current_step.next()
            pass



    @on_event("step/start")
    async def handle_start(self, **kwargs):
        '''
        Event Handler for "step/start".
        It starts the brewing process
        
        :param kwargs: 
        :return: None
        '''
        await self.start()

    @on_event("step/reset")
    async def handle_reset(self, **kwargs):
        '''
        Event Handler for "step/reset".
        Resets the current step
        
        :param kwargs: 
        :return: None
        '''
        await self.model.reset_all_steps()



    @on_event("step/stop")
    async def handle_stop(self,  **kwargs):
        '''
        Event Handler for "step/stop".
        Stops the current step
        
        
        :param kwargs: 
        :return: None
        '''
        if self.current_step is not None:
            self.current_step.stop()

        for key, step in self.cache.items():
            step.state = None

        self.current_step = None



    @on_event("job/step/done")
    async def handle_step_done(self, topic, **kwargs):

        '''
        Event Handler for "step/+/done".
        Starts the next step
        
        :param topic: 
        :param kwargs: 
        :return: 
        '''


        if self.cbpi.shutdown:
            return

        self.cache[self.current_step.id].state = "D"
        step_id = self.current_step.id
        self.current_step = None

        await self.start()



    def _get_manged_fields_as_array(self, type_cfg):

        result = []
        for f in type_cfg.get("properties"):
            result.append(f.get("name"))

        return result

    async def start(self):

        '''
        Start the first step 
        
        :return:None  
        '''

        if self.current_step is None:
            loop = asyncio.get_event_loop()
            open_step = False

            inactive = await self.model.get_by_state("I")
            active = await self.model.get_by_state("A")



            if active is not None:
                active.state = 'D'
                active.end = int(time.time())
                # self.stop_step()
                self.current_step = None
                await self.model.update(**active.__dict__)

            if inactive is not None:
                step_type = self.types["CustomStepCBPi"]

                config = dict(cbpi=self.cbpi, id=inactive.id, name=inactive.name, managed_fields=self._get_manged_fields_as_array(step_type))
                self.current_step = step_type["class"](**config)

                inactive.state = 'A'
                inactive.stepstate = inactive.config
                inactive.start = int(time.time())
                await self.model.update(**inactive.__dict__)
                self.current_job = await self.cbpi.start_job(self.current_step.run(), inactive.name, "step")
            else:
                await self.cbpi.bus.fire("step/berwing/finished")

    async def stop(self):
        pass
