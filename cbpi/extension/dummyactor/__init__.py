import logging
from unittest.mock import MagicMock, patch

from cbpi.api import *


logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
except Exception:
    logger.error("Failed to load RPi.GPIO. Using Mock")
    MockRPi = MagicMock()
    modules = {
        "RPi": MockRPi,
        "RPi.GPIO": MockRPi.GPIO
    }
    patcher = patch.dict("sys.modules", modules)
    patcher.start()
    import RPi.GPIO as GPIO

class CustomActor(CBPiActor):

    # Custom property which can be configured by the user
    @action("test", parameters={})
    def action1(self):

        pass



    def init(self):
        self.state = False
        pass

    def on(self, power=0):
        logger.info("ACTOR %s ON" % self.id)
        self.state = True

    def off(self):
        logger.info("ACTOR %s OFF " % self.id)
        self.state = False

    def get_state(self):

        return self.state


class GPIOActor(CBPiActor):

    # Custom property which can be configured by the user

    gpio = Property.Select("GPIO", options=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27], description="GPIO to which the actor is connected")

    def init(self):
        try:
            GPIO.setup(int(self.gpio), GPIO.OUT)
            GPIO.output(int(self.gpio), 0)
        except Exception as e:
            raise CBPiException("FAILD TO INIT ACTOR")

    def on(self, power=0):

        print("GPIO ON %s" % str(self.gpio))
        GPIO.output(int(self.gpio), 1)
        self.state = True

    def off(self):
        print("GPIO OFF %s" % str(self.gpio))
        GPIO.output(int(self.gpio), 0)
        self.state = False

class GPIORelayBoardActor(CBPiActor):

    # Custom property which can be configured by the user

    gpio = Property.Select("GPIO", options=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27], description="GPIO to which the actor is connected")

    def init(self):
        try:
            GPIO.setup(int(self.gpio), GPIO.OUT)
            GPIO.output(int(self.gpio), 1)
        except Exception as e:
            raise CBPiException("FAILD TO INIT ACTOR")

    def on(self, power=0):

        print("GPIO ON %s" % str(self.gpio))
        GPIO.output(int(self.gpio), 0)
        self.state = True

    def off(self):
        print("GPIO OFF %s" % str(self.gpio))
        GPIO.output(int(self.gpio), 1)
        self.state = False



def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("CustomActor", CustomActor)
