# -*- coding: utf-8 -*-
import asyncio
import random
import re

from aiohttp import web
from cbpi.api import *


@parameters([Property.Number(label="Param1", configurable=True), 
             Property.Text(label="Param2", configurable=True, default_value="HALLO"), 
             Property.Select(label="Param3", options=[1,2,4]), 
             Property.Sensor(label="Param4"), 
             Property.Actor(label="Param5")])
class CustomSensor(CBPiSensor):
    
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
    cbpi.plugin.register("CustomSensor", CustomSensor)
