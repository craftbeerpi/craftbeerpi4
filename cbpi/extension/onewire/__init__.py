# -*- coding: utf-8 -*-
import asyncio
import logging
from aiohttp import web
from cbpi.api import *
import os, threading, time
from subprocess import call
from cbpi.api.dataclasses import NotificationAction, NotificationType

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
                with open('/sys/bus/w1/devices/%s/w1_slave' % self.sensor_name, 'r') as content_file:
                    content = content_file.read()
                    if (content.split('\n')[0].split(' ')[11] == "YES"):
                        temp = float(content.split("=")[-1]) / 1000  # temp in Celcius
                        self.value = temp
            except:
                pass
            
            time.sleep(1)

@parameters([Property.Select(label="Sensor", options=getSensors()), 
             Property.Number(label="offset",configurable = True, default_value = 0, description="Sensor Offset (Default is 0)"),
             Property.Select(label="Interval", options=[1,5,10,30,60], description="Interval in Seconds"),
             Property.Kettle(label="Kettle", description="Reduced logging if Kettle is inactive (only Kettle or Fermenter to be selected)"),
             Property.Fermenter(label="Fermenter", description="Reduced logging in seconds if Fermenter is inactive (only Kettle or Fermenter to be selected)"),
             Property.Number(label="ReducedLogging", configurable=True, description="Reduced logging frequency in seconds if selected Kettle or Fermenter is inactive (default is 60 sec)")
             ])
class OneWire(CBPiSensor):
    
    def __init__(self, cbpi, id, props):
        super(OneWire, self).__init__(cbpi, id, props)
        self.value = 200

    async def start(self):
        await super().start()
        self.name = self.props.get("Sensor")
        self.interval = int(self.props.get("Interval", 60))
        self.offset = float(self.props.get("offset",0))

        self.reducedfrequency=float(self.props.get("ReducedLogging", 60))
        self.lastlog=0
        self.sensor=self.get_sensor(self.id)       
        self.kettleid=self.props.get("Kettle", None)
        self.fermenterid=self.props.get("Fermenter", None)
        self.reducedlogging=True if self.kettleid or self.fermenterid else False

        if self.kettleid is not None and self.fermenterid is not None:
            self.reducedlogging=False
            self.cbpi.notify("OneWire Sensor", "Sensor '" + str(self.sensor.name) + "' cant't have Fermenter and Kettle defined for reduced logging.", NotificationType.WARNING, action=[NotificationAction("OK", self.Confirm)])
        if self.interval >= self.reducedfrequency:
            self.reducedlogging=False
            self.cbpi.notify("OneWire Sensor", "Sensor '" + str(self.sensor.name) + "' has shorter or equal 'reduced logging' compared to regular interval.", NotificationType.WARNING, action=[NotificationAction("OK", self.Confirm)])

        self.t = ReadThread(self.name)
        self.t.daemon = True
        def shutdown():
            shutdown.cb.shutdown()
        shutdown.cb = self.t
        self.t.start()


    async def Confirm(self, **kwargs):
        pass
    
    async def stop(self):
        try:
            self.t.stop()
            self.running = False
        except:
            pass

    async def run(self):

        self.kettle = self.get_kettle(self.kettleid) if self.kettleid is not None else None 
        self.fermenter = self.get_fermenter(self.fermenterid) if self.fermenterid is not None else None
        
        while self.running == True:
            self.TEMP_UNIT=self.get_config_value("TEMP_UNIT", "C")
            if self.TEMP_UNIT == "C": # Report temp in C if nothing else is selected in settings
                self.value = round((self.t.value + self.offset),2)
            else: # Report temp in F if unit selected in settings
                self.value = round((9.0 / 5.0 * self.t.value + 32 + self.offset), 2)           
            self.push_update(self.value)
            if self.reducedlogging:
                await self.logvalue()
            else:
                    logging.info("OneWire {} regular logging".format(self.sensor.name))
                    self.log_data(self.value)
                    self.lastlog = time.time()
            await asyncio.sleep(self.interval)

    async def logvalue(self):
        now=time.time()        
        logging.info("OneWire {} logging subroutine".format(self.sensor.name))    
        if self.kettle is not None:
            try:
                kettlestatus=self.kettle.instance.state
            except:
                kettlestatus=False
            if kettlestatus:
                self.log_data(self.value)
                logging.info("OneWire {} Kettle Active".format(self.sensor.name))
                self.lastlog = time.time()
            else:
                logging.info("OneWire {} Kettle Inactive".format(self.sensor.name))
                if now >= self.lastlog + self.reducedfrequency:
                    self.log_data(self.value)
                    self.lastlog = time.time()
                    logging.info("Logged with reduced freqency")
                    pass   

        if self.fermenter is not None:
            try:
                fermenterstatus=self.fermenter.instance.state
            except:
                fermenterstatus=False
            if fermenterstatus:
                self.log_data(self.value)
                logging.info("OneWire {} Fermenter Active".format(self.sensor.name))
                self.lastlog = time.time()
            else:
                logging.info("OneWire {} Fermenter Inactive".format(self.sensor.name))
                if now >= self.lastlog + self.reducedfrequency:
                    self.log_data(self.value)
                    self.lastlog = time.time()
                    logging.info("Logged with reduced freqency")
                    pass            

    
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
