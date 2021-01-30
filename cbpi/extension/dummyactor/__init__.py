import logging
from unittest.mock import MagicMock, patch

from cbpi.api import *


logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
except Exception:
    logger.error("Failed to load RPi.GPIO. Using Mock")
    MockRPi = MagicMock()
    modules = {
        "RPi": MockRPi,
        "RPi.GPIO": MockRPi.GPIO
    }
    patcher = patch.dict("sys.modules", modules)
    patcher.start()
    import RPi.GPIO as GPIO


@parameters([])
class CustomActor(CBPiActor):
    my_name = ""

    # Custom property which can be configured by the user
    @action("test", parameters={})
    async def action1(self, **kwargs):
        print("ACTION !", kwargs)
        self.my_name = kwargs.get("name")
        pass
    
    def init(self):
        print("INIT")
        self.state = False
        pass

    async def on(self, power=0):
        logger.info("ACTOR 1111 %s ON" % self.id)
        self.state = True

    async def off(self):
        logger.info("ACTOR %s OFF " % self.id)
        self.state = False

    def get_state(self):
        
        return self.state
    
    async def run(self):
        pass

def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("CustomActor", CustomActor)
