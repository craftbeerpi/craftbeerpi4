import asyncio
import time

from cbpi_api import *

from core.controller.crud_controller import CRUDController
from core.database.model import StepModel


class StepController(CRUDController):
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
        self.cbpi.register(self)


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
