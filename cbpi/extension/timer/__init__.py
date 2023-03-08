# -*- coding: utf-8 -*-
from aiohttp import web
import logging
import asyncio
from cbpi.api import *
from cbpi.api import base
from time import strftime, gmtime
from cbpi.api.timer import Timer
from cbpi.api.dataclasses import DataType
from cbpi.api.dataclasses import NotificationAction, NotificationType

logger = logging.getLogger(__name__)
@parameters([])
class AlarmTimer(CBPiSensor):

    def __init__(self, cbpi, id, props):
        super(AlarmTimer, self).__init__(cbpi, id, props)
        self.value = "00:00:00"
        self.datatype=DataType.STRING
        self.timer = None
        self.time=0
        self.stopped=False
        self.sensor=self.get_sensor(self.id)
        
    @action(key="Set Timer", parameters=[Property.Number(label="time", description="Time in Minutes", configurable=True)])
    async def set(self, time = 0,**kwargs):
        self.stopped=False
        self.time = float(time)
        self.value=self.calculate_time(self.time)
        await self.timer.stop()
        self.timer = Timer(int(self.time * 60), on_update=self.on_timer_update, on_done=self.on_timer_done)
        self.timer.start()
        await self.timer.stop()
        self.timer.is_running = False
        logging.info("Set Timer")

    @action(key="Start Timer", parameters=[])
    async def start(self , **kwargs):
        if self.timer is None:
            self.timer = Timer(int(self.time * 60), on_update=self.on_timer_update, on_done=self.on_timer_done)

        if self.timer.is_running is not True:
            self.timer.start()
            self.stopped=False
            self.timer.is_running = True
        else:
            self.cbpi.notify(self.sensor.name,'Timer is already running', NotificationType.WARNING)
        
    @action(key="Stop Timer", parameters=[])
    async def stop(self , **kwargs):
        self.stopped=False
        await self.timer.stop()
        self.timer.is_running = False
        logging.info("Stop Timer")

    @action(key="Reset Timer", parameters=[])
    async def Reset(self , **kwargs):
        self.stopped=False
        await self.timer.stop()
        self.value=self.calculate_time(self.time)
        self.timer = Timer(int(self.time * 60), on_update=self.on_timer_update, on_done=self.on_timer_done)
        self.timer.start()
        await self.timer.stop()
        self.timer.is_running = False
        logging.info("Reset Timer")

    async def on_timer_done(self, timer):
        #self.value = "Stopped"
        if self.stopped is True:
            self.cbpi.notify(self.sensor.name,'Timer done', NotificationType.SUCCESS)

        self.timer.is_running = False
        pass

    async def on_timer_update(self, timer, seconds):
        self.stopped=True
        self.value = Timer.format_time(seconds)

    async def run(self):   
        while self.running is True:
            self.push_update(self.value)
            await asyncio.sleep(1)
            pass

    def get_state(self):
        return dict(value=self.value)
    
    def calculate_time(self, time):
        return strftime("%H:%M:%S", gmtime(time*60))

def setup(cbpi):
    cbpi.plugin.register("AlarmTimer", AlarmTimer)
    pass