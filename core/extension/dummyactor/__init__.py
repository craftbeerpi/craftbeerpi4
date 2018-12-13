import logging

from core.api import CBPiActor, Property, action


class CustomActor(CBPiActor):

    # Custom property which can be configured by the user
    gpio = Property.Number(label="Test")

    def init(self):
        print("#########INIT MY CUSTOM ACTOR")

    def stop(self):
        print("#########STOP MY CUSTOM ACTOR")


    @action(key="name", parameters={})
    def myAction(self):
        pass

    def state(self):
        super().state()

    def off(self):
        print("OFF", self.gpio)

        # Code to swtich the actor off goes here

        self.state = False

    def on(self, power=100):
        print("ON", self.gpio)

        # Code to swtich the actor on goes here

        self.state = True



def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("CustomActor", CustomActor)
