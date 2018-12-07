import time

import asyncio

import logging


class Step(object):

    __dirty = False
    managed_fields = []
    _interval = 1
    _max_exceptions = 2
    _exception_count = 0

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        for a in kwargs:
            super(Step, self).__setattr__(a, kwargs.get(a))
        self.id = kwargs.get("id")
        self.is_stopped = False
        self.is_next = False
        self.start = time.time()

    def running(self):
        if self.is_next is True:
            return False

        if self.is_stopped is True:
            return False

        return True

    async def run(self):

        while self.running():
            try:
                await self.run_cycle()
            except Exception as e:
                logging.exception("Step Error")
                self._exception_count = self._exception_count + 1
                if self._exception_count == self._max_exceptions:
                    self.stop()
            print("INTER",self._interval)
            await asyncio.sleep(self._interval)

            if self.is_dirty():
                # Now we have to store the managed props
                self.reset_dirty()

    async def run_cycle(self):
        print("NOTING IMPLEMENTED")
        pass

    def next(self):
        self.is_next = True

    def stop(self):
        self.is_stopped = True

    def reset(self):
        pass

    def is_dirty(self):
        return self.__dirty

    def reset_dirty(self):
        self.__dirty = False

    def __setattr__(self, name, value):
        if name != "_Step__dirty" and name in self.managed_fields:
            self.__dirty = True
            super(Step, self).__setattr__(name, value)
        else:
            super(Step, self).__setattr__(name, value)