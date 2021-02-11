from cbpi.api import *


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


    async def notify(self, message, type=None):
        self.cbpi.ws.send(dict(topic="notifiaction", type=type, message=message))

