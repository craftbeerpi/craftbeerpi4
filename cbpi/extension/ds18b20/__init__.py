# -*- coding: utf-8 -*-
import asyncio
import threading
import time

from aiohttp import web
from cbpi.api import *

import re
import random


def getSensors():
    try:
        arr = []
        for dirname in os.listdir('/sys/bus/w1/devices'):
            if (dirname.startswith("28") or dirname.startswith("10")):
                cbpi.app.logger.info("Device %s Found (Family: 28/10, Thermometer on GPIO4 (w1))" % dirname)
                arr.append(dirname)
        return arr
    except:
        return []


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
                app.logger.info("READ TEMP")
                ## Test Mode
                if self.sensor_name is None:
                    return
                with open('/sys/bus/w1/devices/w1_bus_master1/%s/w1_slave' % self.sensor_name, 'r') as content_file:
                    content = content_file.read()
                    if (content.split('\n')[0].split(' ')[11] == "YES"):
                        temp = float(content.split("=")[-1]) / 1000  # temp in Celcius
                        self.value = temp
            except:
                pass

            self.value = random.randint(1,100)
            time.sleep(4)

class DS18B20(CBPiSensor):


    sensor_name = Property.Select("Sensor", getSensors(), description="The OneWire sensor address.")
    offset = Property.Number("Offset", True, 0, description="Offset which is added to the received sensor data. Positive and negative values are both allowed.")
    interval = Property.Number(label="interval", configurable=True)

    # Internal runtime variable
    value = 0

    def init(self):
        super().init()
        self.state = True
        self.t = myThread(self.sensor_name)
        def shudown():
            shudown.cb.shutdown()

        shudown.cb = self.t

        self.t.start()

    def get_state(self):
        return self.state

    def get_value(self):

        return self.value

    def get_unit(self):
        return "°%s" % self.get_parameter("TEMP_UNIT", "C")

    def stop(self):
        try:
            self.t.stop()
        except:
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

    cbpi.plugin.register("DS18B20", DS18B20)
