__all__ = ["CBPiActor"]

import logging

from core.api.extension import CBPiExtension
from core.utils.utils import load_config as load
logger = logging.getLogger(__file__)

class CBPiActor(CBPiExtension):

    def __init__(self, cbpi):
        self.id = ""
        self.state = None
        self.name = ""

    def on(self, power):
        pass

    def off(self):
        pass

    def state(self):
        pass