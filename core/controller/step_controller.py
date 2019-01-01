import asyncio
import time

from aiohttp import web
from cbpi_api import *
from cbpi_api.exceptions import CBPiException

from core.controller.crud_controller import CRUDController
from core.database.model import StepModel
from core.http_endpoints.http_api import HttpAPI


class StepHttpAPI(HttpAPI):
    @request_mapping(path="/types", auth_required=False)
    async def get_types(self, request):
        """
        ---
        description: Get all step types
        tags:
        - Step
        responses:
            "200":
                description: successful operation
        """
        return await super().get_types(request)

    @request_mapping(path="/", auth_required=False)
    async def http_get_all(self, request):
        """

        ---
        description: Switch step on
        tags:
        - Step
        parameters:
        - name: "id"
          in: "path"
          description: "step ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
            "405":
                description: invalid HTTP Met
        """
        return await super().http_get_all(request)

    @request_mapping(path="/{id:\d+}", auth_required=False)
    async def http_get_one(self, request):
        """
        ---
        description: Get one step
        tags:
        - Step
        parameters:
        - name: "id"
          in: "path"
          description: "step ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
            "405":
                description: invalid HTTP Met
        """
        return await super().http_get_one(request)

    @request_mapping(path="/", method="POST", auth_required=False)
    async def http_add(self, request):
        """
        ---
        description: Get one step
        tags:
        - Step
        parameters:
        - in: body
          name: body
          description: Created an step
          required: false
          schema:
            type: object
            properties:
              name:
                type: string
              type:
                type: string
              config:
                type: object
        responses:
            "204":
                description: successful operation
        """
        return await super().http_add(request)

    @request_mapping(path="/{id}", method="PUT", auth_required=False)
    async def http_update(self, request):
        """
        ---
        description: Update an step
        tags:
        - Step
        parameters:
        - name: "id"
          in: "path"
          description: "step ID"
          required: true
          type: "integer"
          format: "int64"
        - in: body
          name: body
          description: Update an step
          required: false
          schema:
            type: object
            properties:
              name:
                type: string
              type:
                type: string
              config:
                type: object
        responses:
            "200":
                description: successful operation
        """
        return await super().http_update(request)

    @request_mapping(path="/{id}", method="DELETE", auth_required=False)
    async def http_delete_one(self, request):
        """
        ---
        description: Delete a step
        tags:
        - Step
        parameters:
        - name: "id"
          in: "path"
          description: "Step ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
        """
        return await super().http_delete_one(request)


    @request_mapping(path="/action", auth_required=False)
    async def http_action(self, request):
        """
        ---
        description: Call step action
        tags:
        - Step
        responses:
            "204":
                description: successful operation
        """
        await self.cbpi.bus.fire("step/action", action="test")
        return web.Response(text="OK")

    @request_mapping(path="/start", auth_required=False)
    async def http_start(self, request):
        """
        ---
        description: Start Brewing Process
        tags:
        - Step
        responses:
            "204":
                description: successful operation
        """
        if self.is_running():
            raise CBPiException("Brewing Process Already Running")
        result = await self.cbpi.bus.fire("step/start")
        r = result.get("core.controller.step_controller.handle_start")
        if r[0] is True:
            return web.Response(status=204)
        else:
            raise CBPiException("Failed to start brewing process")


    @request_mapping(path="/reset", auth_required=False)
    async def http_reset(self, request):
        """
        ---
        description: Reset Brewing Process
        tags:
        - Step
        responses:
            "204":
                description: successful operation
        """
        await self.cbpi.bus.fire("step/reset")
        return web.Response(text="OK")

    @request_mapping(path="/next", auth_required=False)
    async def http_next(self, request):
        """
        ---
        description: Start next step
        tags:
        - Step
        responses:
            "204":
                description: successful operation
        """
        await self.cbpi.bus.fire("step/next")
        return web.Response(text="OK")

    @request_mapping(path="/stop", auth_required=False)
    async def http_stop(self, request):
        """
        ---
        description: Stop next step
        tags:
        - Step
        responses:
            "204":
                description: successful operation
        """
        await self.cbpi.bus.fire("step/stop")
        return web.Response(text="OK")

class StepController(StepHttpAPI, CRUDController):
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
        self.current_job = None
        self.cbpi.register(self, "/step")


    async def init(self):
        '''
        Initializer of the the Step Controller. 
        :return: 
        '''
        await super(StepController, self).init()

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
            self.current_job = await self.cbpi.job.start_job(self.current_step.run(), step.name, "step")



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

    @on_event("step/reset")
    async def handle_reset(self, **kwargs):
        '''
        Event Handler for "step/reset".
        Resets the current step
        
        :param kwargs: 
        :return: None
        '''
        if self.current_step is not None:
            await self.stop()
            self.is_stopping = True

        await self.model.reset_all_steps()


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

        if self.is_stopping is not True:
            await self.start()

        self.is_stopping = False

    def _get_manged_fields_as_array(self, type_cfg):

        result = []
        for f in type_cfg.get("properties"):
            result.append(f.get("name"))

        return result

    def is_running(self):
        if self.current_step is not None:
            return True
        else:
            return False

    @on_event("step/start")
    async def start(self, future, **kwargs):

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
                self.current_job = await self.cbpi.job.start_job(self.current_step.run(), inactive.name, "step")
            else:
                await self.cbpi.bus.fire("step/berwing/finished")

        future.set_result(True)

    @on_event("step/stop")
    async def stop(self, **kwargs):
        if self.current_job is not None:
            self.is_stopping = True
            await self.current_job.close()
            await self.model.reset_all_steps()
