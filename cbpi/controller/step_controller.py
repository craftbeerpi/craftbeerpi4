import logging
import time

from cbpi.api import *
from cbpi.controller.crud_controller import CRUDController
from cbpi.database.model import StepModel


class StepController(CRUDController):
    '''
    The Step Controller. This controller is responsible to start and stop the brewing steps.
    
    '''

    model = StepModel

    def __init__(self, cbpi):
        super(StepController, self).__init__(cbpi)
        self.caching = False
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


    async def get_state(self):
        return dict(items=await self.get_all(),types=self.types,is_running=self.is_running(),current_step=self.current_step)

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
    async def next(self, **kwargs):
        '''
        Event Handler for "step/next".
        It start the next step
        
        :param kwargs: 
        :return: None
        '''
        print("REQUEST NEXT")
        self.starttime = time.time()
        if self.current_step is not None and self.is_next is False:
            self.logger.info("Request Next Step to start. Stopping current step")
            self.is_next = True
            self.current_step.stop()
        else:
            self.logger.info("Can Start Next")




    @on_event("job/step/done")
    async def _step_done(self, topic, **kwargs):

        '''
        Event Handler for "step/+/done".
        Starts the next step
        
        :param topic: 
        :param kwargs: 
        :return: 
        '''

        # SHUTDONW DO NOTHING
        self.logger.info("HANDLE DONE IS SHUTDONW %s  IS STOPPING %s IS NEXT %s" % ( self.cbpi.shutdown, self.is_stopping, self.is_next))


        if self.cbpi.shutdown:
            return

        if self.is_stopping:
            self.is_stopping = False
            return
        self.is_next = False
        if self.current_step is not None:
            await self.model.update_state(self.current_step.id, "D", int(time.time()))
            self.current_step = None
        await self.start()



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
    async def start(self, **kwargs):

        '''
        Start the first step 
        
        :return:None  
        '''

        if self.is_running() is False:
            next_step = await self.model.get_by_state("I")

            if next_step is not None:
                step_type = self.types[next_step.type]

                config = dict(cbpi=self.cbpi, id=next_step.id, name=next_step.name, managed_fields=self._get_manged_fields_as_array(step_type))
                self.current_step = step_type["class"](**config)

                next_step.state = 'A'
                next_step.stepstate = next_step.config
                next_step.start = int(time.time())
                await self.model.update(**next_step.__dict__)
                if self.starttime is not None:
                    end = time.time()
                    d = end - self.starttime
                    print("DURATION", d)
                else:
                    print("NORMAL START")
                self.current_job = await self.cbpi.job.start_job(self.current_step.run(), next_step.name, "step")
                await self.cbpi.bus.fire("step/%s/started" % self.current_step.id)
            else:
                await self.cbpi.bus.fire("step/brewing/finished")
        else:
            self.logger.error("Process Already Running")
        print("----------- END")

    @on_event("step/stop")
    async def stop(self, **kwargs):

        if self.current_step is not None:
            self.current_step.stop()
            self.is_stopping = True
            self.current_step = None

        await self.model.reset_all_steps()
        await self.cbpi.bus.fire("step/brewing/stopped")

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
            self.current_step = None
            self.is_stopping = True

        await self.model.reset_all_steps()

    async def sort(self, data):
        await self.model.sort(data)

    async def _pre_add_callback(self, data):
        order = await self.model.get_max_order()
        data["order"] = 1 if order is None else order + 1
        data["state"] = "I"
        return await super()._pre_add_callback(data)





