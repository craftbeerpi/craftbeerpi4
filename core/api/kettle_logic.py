
from core.api.extension import CBPiExtension

class CBPiKettleLogic(CBPiExtension):

    '''
    Base Class for a Kettle logic. 
    '''


    def stop(self):
        '''
        test
        
        
        :return: 
        '''
        pass

    def run(self):
        '''
        This method is running as background process when logic is started.
        Typically a while loop responsible that the method keeps running 
        
            while self.running:
                await asyncio.sleep(1)
        
        :return: 
        '''

        pass