import logging

from core.api import CBPiActor, Property, action, background_task



class CustomActor(CBPiActor):

    name = Property.Number(label="Test")
    name1 = Property.Text(label="Test")
    name2 = Property.Kettle(label="Test")

    @background_task("s1", interval=2)
    async def bg_job(self):
        print("WOOH BG")

    @action(key="name", parameters={})
    def myAction(self):
        pass

    def state(self):
        super().state()

    def off(self):
        print("OFF")
        self.state = False

    def on(self, power=100):

        print("ON")
        self.state = True


    def __init__(self, cbpi=None):

        if cbpi is None:
            return

        print("INIT MY ACTOR111111")
        self.cfg = self.load_config()

        self.logger = logging.getLogger(__file__)
        logging.basicConfig(level=logging.INFO)

        self.logger.info("########WOOHOO MY ACTOR")
        self.cbpi = cbpi


def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("CustomActor", CustomActor)
