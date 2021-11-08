import asyncio
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

mode = GPIO.getmode()
if (mode == None):
    GPIO.setmode(GPIO.BCM)

@parameters([Property.Select(label="GPIO", options=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]), Property.Select(label="Inverted", options=["Yes", "No"],description="No: Active on high; Yes: Active on low")])
class GPIOActor(CBPiActor):

    @action(key="Cusotm Action", parameters=[Property.Number("Value", configurable=True), Property.Kettle("Kettle")])
    async def custom_action(self, **kwargs):
        print("ACTION", kwargs)
        
    
    @action(key="Cusotm Action2", parameters=[Property.Number("Value", configurable=True)])
    async def custom_action2(self, **kwargs):
        print("ACTION2")
        

    def get_GPIO_state(self, state):
        # ON
        if state == 1:
            return 1 if self.inverted == False else 0
        # OFF
        if state == 0:
            return 0 if self.inverted == False else 1

    async def on_start(self):
        self.power = 100
        self.gpio = self.props.GPIO
        self.inverted = True if self.props.get("Inverted", "No") == "Yes" else False
        GPIO.setup(self.gpio, GPIO.OUT)
        GPIO.output(self.gpio, self.get_GPIO_state(0))
        self.state = False

    async def on(self, power = None):
        logger.info("ACTOR %s ON - GPIO %s " %  (self.id, self.gpio))
        GPIO.output(self.gpio, self.get_GPIO_state(1))  
        self.state = True

    async def off(self):
        logger.info("ACTOR %s OFF - GPIO %s " % (self.id, self.gpio))
        GPIO.output(self.gpio, self.get_GPIO_state(0))
        self.state = False

    def get_state(self):
        return self.state
    
    async def run(self):
        while self.running == True:
            await asyncio.sleep(1)
            

@parameters([Property.Select(label="GPIO", options=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]), Property.Number(label="Frequency", configurable=True)])
class GPIOPWMActor(CBPiActor):

    # Custom property which can be configured by the user
    @action("Set Power", parameters=[Property.Number(label="Power", configurable=True,description="Power Setting [0-100]")])
    async def setpower(self,Power = 100 ,**kwargs):
        logging.info(Power)
        self.power=int(Power)
        if self.power < 0:
            self.power = 0
        if self.power > 100:
            self.power = 100           
        item = self.cbpi.actor.find_by_id(self.id)
        item.power = self.power
        await self.set_power(self.power)

    async def on_start(self):
        self.gpio = self.props.get("GPIO", None)
        self.frequency = self.props.get("Frequency", 0.5)
        if self.gpio is not None:
            GPIO.setup(self.gpio, GPIO.OUT)
            GPIO.output(self.gpio, 0)
        self.state = False
        self.power = 100
        self.p = None
        pass

    async def on(self, power = None):
        if power is not None:
            self.power = power
        
        logger.info("PWM ACTOR %s ON - GPIO %s - Frequency %s - Power %s" %  (self.id, self.gpio,self.frequency,self.power))
        try:
            if self.p is None:
                self.p = GPIO.PWM(int(self.gpio), float(self.frequency))
            self.p.start(self.power)
            self.state = True
        except:
            pass

    async def off(self):
        logger.info("PWM ACTOR %s OFF - GPIO %s " % (self.id, self.gpio))
        self.p.ChangeDutyCycle(0)
        self.state = False

    async def set_power(self, power):
        if self.p and self.state == True:
            self.p.ChangeDutyCycle(power)
        await self.cbpi.actor.set_power(self.id,power)
        pass

    def get_state(self):
        return self.state
    
    async def run(self):
        while self.running == True:
            await asyncio.sleep(1)

def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("GPIOActor", GPIOActor)
    cbpi.plugin.register("GPIOPWMActor", GPIOPWMActor)
