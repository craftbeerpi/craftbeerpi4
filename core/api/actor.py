__all__ = ["CBPiActor"]

import logging

from core.api.extension import CBPiExtension

logger = logging.getLogger(__file__)

class CBPiActor(CBPiExtension):

    def on(self, power):
        pass

    def off(self):
        pass

    def state(self):
        pass