import time
import asyncio
import math


class Timer(object):

    def __init__(self, timeout, callback, update = None) -> None:
        super().__init__()
        self.timeout = timeout
        self._timemout = self.timeout
        self._task = None
        self._callback = callback
        self._update = update
        self.start_time = None
        
    async def _job(self):
        self.start_time = time.time()
        self.count = int(round(self._timemout, 0))
        try:
            for seconds in range(self.count, -1, -1):
                if self._update is not None:
                    await self._update(seconds, self.format_time(seconds))
                await asyncio.sleep(1)
            self._callback()
        except asyncio.CancelledError:
            end = time.time()
            duration = end - self.start_time
            self._timemout = self._timemout - duration
                 
    def start(self):
        self._task = asyncio.create_task(self._job())

    async def stop(self):
        self._task.cancel()
        await self._task

    def reset(self):
        if self.is_running is True:
            return
        self._timemout = self.timeout

    def is_running(self):
        return not self._task.done()

    def set_time(self,timeout):
        if self.is_running is True:
            return
        self.timeout = timeout

    def get_time(self):
        return self.format_time(int(round(self._timemout,0)))

    def format_time(self, time):
            pattern = '{0:02d}:{1:02d}:{2:02d}'
            seconds = time % 60
            minutes = math.floor(time / 60) % 60
            hours = math.floor(time / 3600) 
            return pattern.format(hours, minutes, seconds)
