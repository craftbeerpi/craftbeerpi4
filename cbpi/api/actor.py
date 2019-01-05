from abc import ABCMeta

from cbpi.api.extension import CBPiExtension

__all__ = ["CBPiActor"]

import logging


logger = logging.getLogger(__file__)

class CBPiActor(CBPiExtension, metaclass=ABCMeta):

    def init(self):
        pass

    def stop(self):
        pass

    def on(self, power):
        '''
        Code to switch the actor on. Power is provided as integer value  
        
        :param power: power value between 0 and 100 
        :return: None
        '''
        pass

    def off(self):

        '''
        Code to switch the actor off
        
        :return: None 
        '''
        pass

    def state(self):

        '''
        Return the current actor state
        
        :return: 
        '''

        pass

    def reprJSON(self):
        return dict(state=True)