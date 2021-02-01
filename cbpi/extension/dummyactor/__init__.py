import logging
from unittest.mock import MagicMock, patch

from cbpi.api import *

logger = logging.getLogger(__name__)

@parameters([])
class DummyActor(CBPiActor):
    my_name = ""

    # Custom property which can be configured by the user
    @action("test", parameters={})
    async def action1(self, **kwargs):
        print("ACTION !", kwargs)
        self.my_name = kwargs.get("name")
        pass

    async def start(self):
        await super().start()

    async def on(self, power=0):
        logger.info("ACTOR %s ON " %  self.id)
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

    cbpi.plugin.register("DummyActor", DummyActor)
