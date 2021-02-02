# -*- coding: utf-8 -*-
import asyncio
import random
import re
import random
from aiohttp import web
from cbpi.api import *
import os, re, threading, time

class myThread (threading.Thread):

    value = 0


    def __init__(self, sensor_name):
        threading.Thread.__init__(self)
        self.value = 0
        self.sensor_name = sensor_name
        self.runnig = True

    def shutdown(self):
        pass

    def stop(self):
        self.runnig = False

    def run(self):

        while self.runnig:
            try:
                
                print("READ SENSOR")
            except:
                pass

            time.sleep(1)



@parameters([])
class OneWire(CBPiSensor):
    
    def __init__(self, cbpi, id, props):
        super(OneWire, self).__init__(cbpi, id, props)
        self.value = 0


    async def start(self):

        print("START")
        await super().start()
        self.t = myThread("ABC")

        def shudown():
            shudown.cb.shutdown()
        shudown.cb = self.t

        self.t.start()
        pass
    
    async def stop(self):
        try:
            self.t.stop()
        except:
            pass

    async def run(self):

        while self.running is True:
            
            self.push_update(self.value)
            await asyncio.sleep(10)
    
    def get_state(self):
        return dict(value=self.value)


def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''
    cbpi.plugin.register("OneWire", OneWire)
