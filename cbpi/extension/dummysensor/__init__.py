# -*- coding: utf-8 -*-
import asyncio
import random
import re

from aiohttp import web
from cbpi.api import *


class CustomSensor(CBPiSensor):

    # Custom Properties which will can be configured by the user


    interval = Property.Number(label="interval", configurable=True)

    # Internal runtime variable
    value = 0

    @action(key="name", parameters={})
    def myAction(self):
        '''
        Custom Action Exampel
        :return: None
        '''
        pass

    def init(self):
        super().init()
        self.state = True

    def get_state(self):
        return self.state

    def get_value(self):

        return self.value

    def get_unit(self):
        return "°%s" % self.get_parameter("TEMP_UNIT", "C")

    def stop(self):
        pass

    async def run(self, cbpi):
        self.value = 0
        while True:
            await asyncio.sleep(self.interval)
            self.value = random.randint(1,101)
            self.log_data(self.value)
            await cbpi.bus.fire("sensor/%s/data" % self.id, value=self.value)

@parameters([Property.Number(label="Param1", configurable=True), 
             Property.Text(label="Param2", configurable=True, default_value="HALLO"), 
             Property.Select(label="Param3", options=[1,2,4]), 
             Property.Sensor(label="Param4"), 
             Property.Actor(label="Param5")])
class CustomSensor2(CBPiSensor2):
    
    @action(key="Test", parameters=[])
    async def action1(self, **kwargs):
        print("ACTION!", kwargs)

    @action(key="Test1", parameters=[])
    async def action2(self, **kwargs):
        print("ACTION!", kwargs)
    
    @action(key="Test2", parameters=[])
    async def action3(self, **kwargs):

        print("ACTION!", kwargs)



    async def run(self):

        while self.running is True:
            print("HALLO")
            await asyncio.sleep(1)
    

def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''
    cbpi.plugin.register("CustomSensor2", CustomSensor2)
    #cbpi.plugin.register("CustomSensor", CustomSensor)
