import time
import asyncio
import logging
from abc import abstractmethod,ABCMeta


class CBPiSimpleStep(metaclass=ABCMeta):

    __dirty = False
    managed_fields = []
    _interval = 0.1
    _max_exceptions = 2
    _exception_count = 0

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        for a in kwargs:
            super(CBPiSimpleStep, self).__setattr__(a, kwargs.get(a))
        self.id = kwargs.get("id")
        self.is_stopped = False
        self.is_next = False
        self.start = time.time()

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
                    #step_controller.model.update_step_state(step_controller.current_step.id, state)

                    await self.cbpi.step.model.update_step_state(self.id, state)

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