from cbpi_api import *

class NotificationController():
    '''
    This the notification controller
    '''

    def __init__(self, cbpi):
        '''
        Initializer
        
        :param cbpi: the cbpi server object
        '''
        self.cbpi = cbpi
        self.cbpi.register(self)


    @on_event(topic="notification/#")
    async def _on_event(self, key, message, type, **kwargs):
        self.cbpi.ws.send("YES")