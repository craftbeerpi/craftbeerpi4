import time

import asyncio

import logging


class Step(object):

    __dirty = False
    managed_fields = []
    _interval = 0.1

    def __init__(self, *args, **kwargs):
        self.logger = logging.getLogger(__name__)
        for a in kwargs:
            super(Step, self).__setattr__(a, kwargs.get(a))
        self.id = kwargs.get("id")
        self.stop = False
        self.start = time.time()

    def running(self):
        if self.stop is False:
            return False

        return True

    async def _run(self):
        i = 0
        while i < 5:
            try:
                await self.run()
            except Exception as e:
                pass
                #logging.exception("Step Error")
            print("INTER",self._interval)
            await asyncio.sleep(self._interval)
            i = i + 1
            if self.is_dirty():
                # Now we have to store the managed props
                self.reset_dirty()

    async def run(self):
        print("NOTING IMPLEMENTED")
        pass

    def stop(self):
        pass

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