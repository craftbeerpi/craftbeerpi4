import asyncio
import json
import logging
import time
from abc import ABCMeta, abstractmethod
from enum import Enum

from cbpi.api.base import CBPiBase
from cbpi.api.config import ConfigType

__all__ = ["StepResult", "StepState", "StepMove", "CBPiStep"]

from enum import Enum

class StepResult(Enum):
    STOP=1
    NEXT=2
    DONE=3
    ERROR=4

class StepState(Enum):
    INITIAL="I"
    DONE="D"
    ACTIVE="A"
    ERROR="E"
    STOP="S"

class StepMove(Enum):
    UP=-1
    DOWN=1

class CBPiStep(CBPiBase):

    def __init__(self, cbpi, id, name, props, on_done) -> None:
        self.name = name
        self.cbpi = cbpi
        self.id = id
        self.timer = None
        self._done_callback = on_done
        self.props = props
        self.cancel_reason: StepResult = None
        self.summary = ""

    def _done(self, task):
        self._done_callback(self, task.result())

    async def start(self):
        self.task = asyncio.create_task(self._run())
        self.task.add_done_callback(self._done)

    async def next(self):   
        self.cancel_reason = StepResult.NEXT
        self.task.cancel()
        await self.task

    async def stop(self):   
        try:
            self.cancel_reason = StepResult.STOP
            self.task.cancel()
            await self.task
        except:
            pass

    async def reset(self):
        pass

    async def on_props_update(self, props):
        self.props = {**self.props, **props}

    async def save_props(self):
        await self.cbpi.step.save()
    
    async def push_update(self):
        self.cbpi.step.push_udpate()

    async def on_start(self):
        pass

    async def on_stop(self):
        pass

    async def _run(self):
        try:
            await self.on_start()
            await self.run()
            self.cancel_reason = StepResult.DONE
        except asyncio.CancelledError as e:        
            pass
        finally:
            await self.on_stop()
        
        return self.cancel_reason

    @abstractmethod
    async def run(self):
        pass

    def __str__(self):
        return "name={} props={}, type={}".format(self.name, self.props, self.__class__.__name__)
