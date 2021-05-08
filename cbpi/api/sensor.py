import asyncio
import logging
from abc import abstractmethod, ABCMeta
from cbpi.api.extension import CBPiExtension


from cbpi.api.base import CBPiBase


class CBPiSensor(CBPiBase, metaclass=ABCMeta):
    def __init__(self, cbpi, id, props):
        self.cbpi = cbpi
        self.id = id
        self.props = props
        self.logger = logging.getLogger(__file__)
        self.data_logger = None
        self.state = False
        self.running = False

    def init(self):
        pass

    def log_data(self, value):
        self.cbpi.log.log_data(self.id, value)

    def get_state(self):
        pass

    def get_value(self):
        pass

    def get_unit(self):
        pass

    def push_update(self, value):
        try:
            self.cbpi.ws.send(dict(topic="sensorstate", id=self.id, value=value))
        except:
            logging.error("Faild to push sensor update")

    async def start(self):
        pass

    async def stop(self):
        pass

    async def on_start(self):
        pass

    async def on_stop(self):
        pass

    async def run(self):
        pass

    async def _run(self):

        try:
            await self.on_start()
            self.cancel_reason = await self.run()
        except asyncio.CancelledError as e:
            pass
        finally:
            await self.on_stop()
