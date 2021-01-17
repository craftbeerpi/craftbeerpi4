import json
import time
import asyncio
import logging
from abc import abstractmethod, ABCMeta
import logging

class CBPiStep(metaclass=ABCMeta):
    def __init__(self, cbpi, id, name, props) :
        self.cbpi = cbpi
        self.props = {"wohoo": 0, "count": 5, **props}
        self.id = id
        self.name = name
        self.status = 0
        self.running = False
        self.stop_reason = None
        self.pause = False
        self.task = None
        self._exception_count = 0
        self._max_exceptions = 2
        self.state_msg = "No state"

    def get_state(self):
        return self.state_msg

    def stop(self):
        self.stop_reason = "STOP"
        self.running = False
        
    def start(self):
        self.running = True
        self.stop_reason = None
    
    def next(self):
        self.stop_reason = "NEXT"
        self.running = False

    async def reset(self): 
        pass

    async def update(self, props):
        await self.cbpi.step2.update_props(self.id, props)

    async def run(self): 
        while self.running:
            try:
                await self.execute()
            except:
                self._exception_count += 1
                logging.error("Step has thrown exception")
                if self._exception_count >= self._max_exceptions:
                    self.stop_reason = "MAX_EXCEPTIONS"
                    return (self.id, self.stop_reason)
            await asyncio.sleep(1)
            
        return (self.id, self.stop_reason)

    @abstractmethod
    async def execute(self):
        pass

class CBPiSimpleStep(metaclass=ABCMeta):

    managed_fields = []

    def __init__(self, cbpi="", managed_fields=[], id="", name="", *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        self._exception_count = 0
        self._interval = 0.1
        self._max_exceptions = 2
        self.__dirty = False
        self.cbpi = cbpi
        self.id = id
        self.name = name

        if managed_fields:
            self.managed_fields = managed_fields
            for a in managed_fields:
                super(CBPiSimpleStep, self).__setattr__(a, kwargs.get(a, None))

        self.is_stopped = False
        self.is_next = False
        self.start = time.time()

        self.logger.info(self.__repr__())

    def __repr__(self) -> str:
        mf = {}
        has_cbpi = True if self.cbpi is not None else  False
        for f in self.managed_fields:
            mf[f] = super(CBPiSimpleStep, self).__getattribute__(f)
        return json.dumps(dict(type=self.__class__.__name__, id=self.id, name=self.name, has_link_to_cbpi=has_cbpi, managed_fields=mf))

    def get_status(self):
        pass

    def running(self):
        '''
        Method checks if the step should continue running. 
        The method will return False if the step is requested to stop or the next step should start
        
        :return: True if the step is running. Otherwise False.
        '''
        if self.is_next is True:
            return False

        if self.is_stopped is True:
            return False

        return True

    async def run(self):

        #while self.running():
        #    print(".... Step %s ...." % self.id)
        #    await asyncio.sleep(0.1)
        '''
        This method in running in the background. It invokes the run_cycle method in the configured interval
        It checks if a managed variable was modified in the last exection cycle. If yes, the method will persisit the new value of the
        managed property
        
        :return: None 
        '''

        while self.running():

            try:
                await self.run_cycle()
            except Exception as e:
                logging.exception("CBPiSimpleStep Error")
                self._exception_count = self._exception_count + 1
                if self._exception_count == self._max_exceptions:
                    self.logger.error("Step Exception limit exceeded. Stopping Step")
                    self.stop()

            await asyncio.sleep(self._interval)

            if self.is_dirty():
                # Now we have to store the managed props
                state = {}
                for field in self.managed_fields:

                    state[field] = self.__getattribute__(field)

                await self.cbpi.step.model.update_step_state(self.id, state)
                await self.cbpi.bus.fire("step/update")
                self.reset_dirty()


    @abstractmethod
    async def run_cycle(self):
        '''
        This method is executed in the defined interval. 
        That the place to put your step logic.
        The method need to be overwritten in the Ccstom step implementaion
        
        :return: None 
        '''

        print("NOTING IMPLEMENTED")
        pass

    def next(self):

        '''
        Request to stop the the step
        
        :return: None 
        '''

        self.is_next = True

    def stop(self):
        '''
        Request to stop the step
        
        :return: None 
        '''
        self.is_stopped = True

    def reset(self):
        '''
        Reset the step. This method needs to be overwritten by the custom step implementation
        
        :return: None 
        '''
        pass

    def is_dirty(self):

        '''
        Check if a managed variable has a new value
        
        :return: True if at least one managed variable has a new value assigend. Otherwise False
        '''
        return self.__dirty

    def reset_dirty(self):
        '''
        Reset the dirty flag
        
        :return: 
        '''

        self.__dirty = False

    def __setattr__(self, name, value):
        if name != "_Step__dirty" and name in self.managed_fields:
            self.__dirty = True
            super(CBPiSimpleStep, self).__setattr__(name, value)
        else:
            super(CBPiSimpleStep, self).__setattr__(name, value)
