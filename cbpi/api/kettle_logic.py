from cbpi.api.extension import CBPiExtension


class CBPiKettleLogic(CBPiExtension):

    '''
    Base Class for a Kettle logic. 
    '''

    def init(self):
        '''
        Code which will be executed when the logic is initialised. Needs to be overwritten by the implementing logic
        
        :return: None
        '''
        pass

    def stop(self):
        '''
        Code which will be executed when the logic is stopped. Needs to be overwritten by the implementing logic
        
        
        :return: None
        '''
        pass

    def run(self):
        '''
        This method is running as background process when logic is started.
        Typically a while loop responsible that the method keeps running 
        
            while self.running:
                await asyncio.sleep(1)
        
        :return: None
        '''

        pass