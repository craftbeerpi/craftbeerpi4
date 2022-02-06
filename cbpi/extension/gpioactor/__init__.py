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

@parameters([Property.Select(label="GPIO", options=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27]), 
             Property.Select(label="Inverted", options=["Yes", "No"],description="No: Active on high; Yes: Active on low"),
             Property.Select(label="SamplingTime", options=[2,5],description="Time in seconds for power base interval (Default:5)")])
class GPIOActor(CBPiActor):

    # Custom property which can be configured by the user
    @action("Set Power", parameters=[Property.Number(label="Power", configurable=True,description="Power Setting [0-100]")])
    async def setpower(self,Power = 100 ,**kwargs):
        self.power=int(Power)
        if self.power < 0:
            self.power = 0
        if self.power > 100:
            self.power = 100           
        await self.set_power(self.power)      

    def get_GPIO_state(self, state):
        # ON
        if state == 1:
            return 1 if self.inverted == False else 0
        # OFF
        if state == 0:
            return 0 if self.inverted == False else 1

    async def on_start(self):
        self.power = None
        self.gpio = self.props.GPIO
        self.inverted = True if self.props.get("Inverted", "No") == "Yes" else False
        self.sampleTime = int(self.props.get("SamplingTime", 5)) 
        GPIO.setup(self.gpio, GPIO.OUT)
        GPIO.output(self.gpio, self.get_GPIO_state(0))
        self.state = False

    async def on(self, power = None):
        if power is not None:
            self.power = power
        else: 
            self.power = 100
        await self.set_power(self.power)

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
            if self.state == True:
                heating_time=self.sampleTime * (self.power / 100)
                wait_time=self.sampleTime - heating_time
                if heating_time > 0:
                    #logging.info("Heating Time: {}".format(heating_time))
                    GPIO.output(self.gpio, self.get_GPIO_state(1))
                    await asyncio.sleep(heating_time)
                if wait_time > 0:
                    #logging.info("Wait Time: {}".format(wait_time))
                    GPIO.output(self.gpio, self.get_GPIO_state(0))
                    await asyncio.sleep(wait_time)
            else:
                await asyncio.sleep(1)

    async def set_power(self, power):
        self.power = power
        await self.cbpi.actor.actor_update(self.id,power)
        pass
            

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
        await self.set_power(self.power)

    async def on_start(self):
        self.gpio = self.props.get("GPIO", None)
        self.frequency = self.props.get("Frequency", 0.5)
        if self.gpio is not None:
            GPIO.setup(self.gpio, GPIO.OUT)
            GPIO.output(self.gpio, 0)
        self.state = False
        self.power = None
        self.p = None
        pass

    async def on(self, power = None):
        logging.info("PWM Actor Power: {}".format(power))
        if power is not None:
            self.power = power
        else:
            self.power = 100

        logging.info("PWM Final Power: {}".format(self.power))    
        
        logger.info("PWM ACTOR %s ON - GPIO %s - Frequency %s - Power %s" %  (self.id, self.gpio,self.frequency,self.power))
        try:
            if self.p is None:
                self.p = GPIO.PWM(int(self.gpio), float(self.frequency))
            self.p.start(self.power)
            self.state = True
            await self.cbpi.actor.actor_update(self.id,self.power)
        except:
            pass

    async def off(self):
        logger.info("PWM ACTOR %s OFF - GPIO %s " % (self.id, self.gpio))
        self.p.ChangeDutyCycle(0)
        self.state = False

    async def set_power(self, power):
        if self.p and self.state == True:
            self.p.ChangeDutyCycle(power)
        await self.cbpi.actor.actor_update(self.id,power)
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
