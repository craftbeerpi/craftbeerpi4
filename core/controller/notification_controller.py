from core.api.decorator import on_event


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
    def on_event(self, key, message, type, **kwargs):

        print("EVENT RECHEICVED", kwargs)
        self.cbpi.ws.send("YES")