# -*- coding: utf-8 -*-
import asyncio
from aiohttp import web
from cbpi.api import *

import re
import random
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


def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("CustomSensor", CustomSensor)
