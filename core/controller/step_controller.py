import asyncio
from aiohttp import web
from core.api import on_event, request_mapping
from core.controller.crud_controller import CRUDController
from core.database.model import StepModel
from core.http_endpoints.http_api import HttpAPI


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
        pass

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


        if self.current_step is not None:
            self.current_task.cancel()
            self.current_step.reset()

            self.steps[self.current_step.id]["state"] = None
            self.current_step = None
            self.current_task = None
            await self.start()

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

    @on_event("step/+/done")
    async def handle_done(self, topic, **kwargs):

        '''
        Event Handler for "step/+/done".
        Starts the next step
        
        :param topic: 
        :param kwargs: 
        :return: 
        '''
        await self.start()

    def _step_done(self, task):

        if task.cancelled() == False:
            self.cache[self.current_step.id].state = "D"
            step_id = self.current_step.id
            self.current_step = None
            self.cbpi.bus.sync_fire("step/%s/done" % step_id)

    def _get_manged_fields_as_array(self, type_cfg):
        print("tYPE", type_cfg)
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
            for key, step in self.cache.items():
                if step.state is None:
                    step_type = self.types["CustomStepCBPi"]
                    print("----------")
                    print(step_type)
                    print("----------")
                    config = dict(cbpi = self.cbpi, id=key, name=step.name, managed_fields=self._get_manged_fields_as_array(step_type))
                    self.current_step = step_type["class"](**config)
                    self.current_task = loop.create_task(self.current_step.run())
                    self.current_task.add_done_callback(self._step_done)
                    open_step = True
                    break
            if open_step == False:
                await self.cbpi.bus.fire("step/berwing/finished")

    async def stop(self):
        pass
