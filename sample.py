

from abc import abstractmethod
import asyncio
from asyncio import tasks
from cbpi.extension.mashstep import MyStep
from cbpi.controller.step_controller import StepController
from cbpi.extension.gpioactor import GPIOActor
from cbpi.api.dataclasses import Actor, Props, Step
from cbpi.controller.basic_controller2 import BasicController
import time
import math 
import json
from dataclasses import dataclass

from unittest.mock import MagicMock, patch


async def main():
    cbpi = MagicMock()
    cbpi.sensor.get_value.return_value = 99
    app = MagicMock()

    types = {"GPIOActor":{"name": "GPIOActor", "class": GPIOActor, "properties": [], "actions": []}}
    
    
    controller = StepController(cbpi)
    controller.types = types = {"MyStep":{"name": "MyStep", "class": MyStep, "properties": [], "actions": []}}

    controller.load()
    await controller.stop()
    await controller.reset_all()
    

    await controller.start()

    
    #await controller.start()
    await asyncio.sleep(2)
    await controller.next()
    await asyncio.sleep(2)
    

if __name__ == "__main__":
    

    asyncio.run(main())


'''
class Timer(object):

    def __init__(self, timeout, on_done = None, on_update = None) -> None:
        super().__init__()
        self.timeout = timeout
        self._timemout = self.timeout
        self._task = None
        self._callback = on_done
        self._update = on_update
        self.start_time = None
    
    def done(self, task):
        if self._callback is not None:
            asyncio.create_task(self._callback(self))

    async def _job(self):
        self.start_time = time.time()
        self.count = int(round(self._timemout, 0))
        try:
            for seconds in range(self.count, 0, -1):
                if self._update is not None:
                    await self._update(self,seconds)
                await asyncio.sleep(1)
            
        except asyncio.CancelledError:
            end = time.time()
            duration = end - self.start_time
            self._timemout = self._timemout - duration
            
                 
    def start(self):
        self._task = asyncio.create_task(self._job())
        self._task.add_done_callback(self.done)

    async def stop(self):
        print(self._task.done())
        if self._task.done() is False:
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

    @classmethod
    def format_time(cls, time):
            pattern = '{0:02d}:{1:02d}:{2:02d}'
            seconds = time % 60
            minutes = math.floor(time / 60) % 60
            hours = math.floor(time / 3600) 
            return pattern.format(hours, minutes, seconds)

from enum import Enum

class StepResult(Enum):
    STOP=1
    NEXT=2
    DONE=3

class Step():

    def __init__(self, name, props, on_done) -> None:
        self.name = name
        self.timer = None
        self._done_callback = on_done
        self.props = props
        self.cancel_reason: StepResult = None

    def _done(self, task):
        print("HALLO")
        self._done_callback(self, task.result())

    async def start(self):
        self.task = asyncio.create_task(self._run())
        self.task.add_done_callback(self._done)

    async def next(self):   
        self.cancel_reason = StepResult.NEXT
        self.task.cancel()
        await self.task

    async def stop(self):   
        self.cancel_reason = StepResult.STOP
        self.task.cancel()
        await self.task
    async def reset(self):
        pass

    async def on_props_update(self, props):
        self.props = {**self.props, **props}

    async def save_props(self, props):
        pass
    
    async def push_state(self, msg):
        pass

    

    async def on_start(self):
        pass

    async def on_stop(self):
        pass

    async def _run(self):

        try:
            await self.on_start()
            self.cancel_reason = await self.run()
        except asyncio.CancelledError as e:
            pass
        finally:
            await self.on_stop()
        return self.cancel_reason

    @abstractmethod
    async def run(self):
        pass


class MyStep(Step):

    async def timer_update(self, timer, seconds):
        print(Timer.format_time(seconds))

    async def timer_done(self, timer):
        print("TIMER DONE")
        await self.next()
    async def on_start(self):
        if self.timer is None:
            self.timer = Timer(20, on_done=self.timer_done, on_update=self.timer_update)
            self.timer.start()

    async def on_stop(self):
        await self.timer.stop()

    async def run(self):
        for i in range(10):
            print("RUNNING")
            await asyncio.sleep(1)
        await self.timer.stop()
        return StepResult.DONE
            

'''
