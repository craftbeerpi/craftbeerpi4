# -*- coding: utf-8 -*-
import asyncio
import random
import re
import random
from aiohttp import web
from cbpi.api import *
import os, re, threading, time
from subprocess import call


def getSensors():
    try:
        arr = []
        for dirname in os.listdir('/sys/bus/w1/devices'):
            if (dirname.startswith("28") or dirname.startswith("10")):
                arr.append(dirname)
        return arr
    except:
        return []


class ReadThread (threading.Thread):

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
                if self.sensor_name is None:
                    return
                with open('/sys/bus/w1/devices/w1_bus_master1/%s/w1_slave' % self.sensor_name, 'r') as content_file:
                    content = content_file.read()
                    if (content.split('\n')[0].split(' ')[11] == "YES"):
                        temp = float(content.split("=")[-1]) / 1000  # temp in Celcius
                        self.value = temp
            except:
                pass
            
            time.sleep(1)

@parameters([Property.Select(label="Sensor", options=getSensors()), Property.Select(label="Interval", options=[1,5,10,30,60], description="Interval in Seconds")])
class OneWire(CBPiSensor):
    
    def __init__(self, cbpi, id, props):
        super(OneWire, self).__init__(cbpi, id, props)
        self.value = 0

    async def start(self):
        await super().start()
        self.name = self.props.get("Sensor")
        self.interval = self.props.get("Interval", 60)
        self.t = ReadThread(self.name)
        self.t.daemon = True
        def shudown():
            shudown.cb.shutdown()
        shudown.cb = self.t
        self.t.start()
    
    async def stop(self):
        try:
            self.t.stop()
            self.running = False
        except:
            pass

    async def run(self):
        while True:
            self.value = self.t.value
            self.log_data(self.value)
            self.push_update(self.value)
            await asyncio.sleep(self.interval)
    
    def get_state(self):
        return dict(value=self.value)


def setup(cbpi):
    cbpi.plugin.register("OneWire", OneWire)
    try:
        # Global Init
        call(["modprobe", "w1-gpio"])
        call(["modprobe", "w1-therm"])
    except Exception as e:
        pass
