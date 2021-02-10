import json
import time
import asyncio
import logging
from abc import abstractmethod, ABCMeta
import logging
from cbpi.api.config import ConfigType
from cbpi.api.base import CBPiBase
from enum import Enum
__all__ = ["Stop_Reason", "CBPiStep"]
class Stop_Reason(Enum):
    STOP = 1
    NEXT = 2


class CBPiStep(CBPiBase, metaclass=ABCMeta):
    def __init__(self, cbpi, id, name, props) :
        self.cbpi = cbpi
        self.props = {**props}
        self.id = id
        self.name = name
        self.status = 0
        self.running = False
        self.stop_reason = None
        self.pause = False
        self.task = None
        self._task = None
        self._exception_count = 0
        self._max_exceptions = 2
        self.state_msg = ""

    def get_state(self):
        return self.state_msg

    def push_update(self):
        self.cbpi.step.push_udpate()

    async def stop(self):
        self.stop_reason = Stop_Reason.STOP
        self._task.cancel()
        await self._task

    async def start(self):
        self.stop_reason = None
        self._task = asyncio.create_task(self.run())
        self._task.add_done_callback(self.cbpi.step.done)
        
    async def next(self):
        self.stop_reason = Stop_Reason.NEXT
        self._task.cancel()

    async def reset(self): 
        pass
    
    

    def on_props_update(self, props):
        self.props = props

    async def update(self, props):
        await self.cbpi.step.update_props(self.id, props)

    async def run(self): 
        try:
            while True:
                try:
                    await self.execute()
                except asyncio.CancelledError as e:
                    raise e
                except Exception as e:
                    self._exception_count += 1
                    logging.error("Step has thrown exception")
                    if self._exception_count >= self._max_exceptions:
                        self.stop_reason = "MAX_EXCEPTIONS"
                        return (self.id, self.stop_reason)
        except asyncio.CancelledError as e:
            return self.id, self.stop_reason
            
        
    @abstractmethod
    async def execute(self):
        pass
   

