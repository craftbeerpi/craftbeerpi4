from core.api.decorator import on_event
from core.api.extension import CBPiExtension

class MyComp(CBPiExtension):

    def __init__(self, cbpi):
        '''
        Initializer
        
        :param cbpi: 
        '''
        self.cbpi = cbpi
        # register for bus events
        self.cbpi.register_events(self)

    @on_event(topic="actor/#")
    def listen(self, **kwargs):
        print("Test", kwargs)

def setup(cbpi):
    '''
    Setup method is invoked during startup
    
    :param cbpi: the cbpi core object
    :return: 
    '''
    # regsiter the component to the core
    cbpi.plugin.register("MyComp", MyComp)