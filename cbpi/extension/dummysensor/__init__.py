# -*- coding: utf-8 -*-
import asyncio
import random
import re
import random
from aiohttp import web
from cbpi.api import *


@parameters([])
class CustomSensor(CBPiSensor):
    
    def __init__(self, cbpi, id, props):
        super(CustomSensor, self).__init__(cbpi, id, props)
        self.value = 0
    async def run(self):

        while self.running == True:
            self.value = random.randint(10,100)
            self.log_data(self.value)
            
            self.push_update(self.value)
            await asyncio.sleep(1)
    def get_state(self):
        return dict(value=self.value)


def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''
    cbpi.plugin.register("CustomSensor", CustomSensor)
