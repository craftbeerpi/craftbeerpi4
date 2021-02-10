from cbpi.api.base import CBPiBase
from cbpi.api.extension import CBPiExtension
from abc import ABCMeta
import logging
import asyncio



class CBPiKettleLogic(CBPiBase, metaclass=ABCMeta):

    def __init__(self, cbpi, id, props):
        self.cbpi = cbpi
        self.id = id
        self.props = props
        self.state = False  
        self.running = False

    def init(self):
        pass

    async def run(self):
        self.state = True
        while self.running:
            await asyncio.sleep(1)
        self.state = False
        
    def get_state(self):
        return dict(running=self.running)

    async def start(self):
        self.running = True

    async def stop(self):
        self.task.cancel()
        await self.task
