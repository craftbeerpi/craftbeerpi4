from cbpi_api import *


class NotificationController(object):
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
    async def _on_event(self, key, message, type=None, **kwargs):
        self.cbpi.ws.send(dict(key=message))

