import logging

from core.api import CBPiActor, Property, action, background_task



class CustomActor(CBPiActor):


    gpio = Property.Number(label="Test")


    @action(key="name", parameters={})
    def myAction(self):
        pass

    def state(self):
        super().state()

    def off(self):
        print("OFF", self.gpio)
        self.state = False

    def on(self, power=100):

        print("ON", self.gpio)
        self.state = True



def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("CustomActor", CustomActor)
