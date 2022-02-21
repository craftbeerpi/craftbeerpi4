import asyncio

from cbpi.api import parameters, Property, action
from cbpi.api.step import StepResult, CBPiFermentationStep
from cbpi.api.timer import Timer
from datetime import datetime
import time
from voluptuous.schema_builder import message
from cbpi.api.dataclasses import NotificationAction, NotificationType
from cbpi.api.dataclasses import Kettle, Props, Fermenter
from cbpi.api import *
import logging
from socket import timeout
from typing import KeysView
from cbpi.api.config import ConfigType
from cbpi.api.base import CBPiBase
import numpy as np
import warnings



@parameters([Property.Text(label="Notification",configurable = True, description = "Text for notification"),
             Property.Select(label="AutoNext",options=["Yes","No"], description="Automatically move to next step (Yes) or pause after Notification (No)")])
class FermenterNotificationStep(CBPiFermentationStep):

    async def NextStep(self, **kwargs):
        await self.next()

    async def on_timer_done(self,timer):
        self.summary = self.props.get("Notification","")

        if self.AutoNext == True:
            self.cbpi.notify(self.name, self.props.get("Notification",""), NotificationType.INFO)
            await self.next()
        else:
            self.cbpi.notify(self.name, self.props.get("Notification",""), NotificationType.INFO, action=[NotificationAction("Next Step", self.NextStep)])
            await self.push_update()

    async def on_timer_update(self,timer, seconds):
        await self.push_update()

    async def on_start(self):
        self.summary=""
        self.AutoNext = False if self.props.get("AutoNext", "No") == "No" else True
        if self.timer is None:
            self.timer = Timer(1 ,on_update=self.on_timer_update, on_done=self.on_timer_done)
        await self.push_update()

    async def on_stop(self):
        await self.timer.stop()
        self.summary = ""
        await self.push_update()

    async def run(self):
        while self.running == True:
            await asyncio.sleep(1)
            if self.timer.is_running is not True:
                self.timer.start()
                self.timer.is_running = True

        return StepResult.DONE

@parameters([Property.Number(label="Temp", configurable=True),
             Property.Sensor(label="Sensor"),
             Property.Text(label="Notification",configurable = True, description = "Text for notification when Temp is reached"),
             Property.Select(label="AutoMode",options=["Yes","No"], description="Switch Fermenterlogic automatically on and off -> Yes")])
class FermenterTargetTempStep(CBPiFermentationStep):

    async def NextStep(self, **kwargs):
        return StepResult.DONE
        #await self.next(self.fermenter)

    async def on_timer_done(self,timer):
        self.summary = ""
        self.fermenter.target_temp = 0
        await self.push_update()
        if self.AutoMode == True:
            await self.setAutoMode(False)
        self.cbpi.notify(self.name, self.props.get("Notification","Target Temp reached. Please add malt and klick next to move on."))
        await self.next()

    async def on_timer_update(self,timer, seconds):
        await self.push_update()

    async def on_start(self):
        self.AutoMode = True if self.props.get("AutoMode","No") == "Yes" else False
        self.starttemp= self.get_sensor_value(self.props.get("Sensor", None)).get("value")    
        if self.fermenter is not None:
            self.fermenter.target_temp = int(self.props.get("Temp", 0))
        if self.AutoMode == True:
            await self.setAutoMode(True)
        self.summary = "Waiting for Target Temp"
        if self.fermenter is not None and self.timer is None:
            self.timer = Timer(1 ,on_update=self.on_timer_update, on_done=self.on_timer_done)
        await self.push_update()

    async def on_stop(self):
        await self.timer.stop()
        self.summary = ""
        if self.AutoMode == True:
            await self.setAutoMode(False)
        await self.push_update()

    async def run(self):
        if self.fermenter.target_temp >= self.starttemp:
            while self.running == True:
                sensor_value = self.get_sensor_value(self.props.get("Sensor", None)).get("value")
                if sensor_value >= int(self.props.get("Temp",0)) and self.timer.is_running is not True:
                    self.timer.start()
                    self.timer.is_running = True
                await asyncio.sleep(1)
        else:
            while self.running == True:
                sensor_value = self.get_sensor_value(self.props.get("Sensor", None)).get("value")
                if sensor_value <= int(self.props.get("Temp",0)) and self.timer.is_running is not True:
                    self.timer.start()
                    self.timer.is_running = True
                await asyncio.sleep(1)
        await self.push_update()
        return StepResult.DONE

    async def reset(self):
        self.timer = Timer(1 ,on_update=self.on_timer_update, on_done=self.on_timer_done)

    async def setAutoMode(self, auto_state):
        try:
            if (self.fermenter.instance is None or self.fermenter.instance.state == False) and (auto_state is True):
                await self.fermenter.instance.toggle(self.fermenter.id)
            elif (self.fermenter.instance.state == True) and (auto_state is False):
                await self.fermenter.instance.stop(self.fermenter.id)
            await self.push_update()

        except Exception as e:
            logging.error("Failed to switch on FermenterLogic {} {}".format(self.fermenter.id, e))


@parameters([Property.Number(label="Timer", description="Time in Minutes", configurable=True), 
             Property.Number(label="Temp", configurable=True),
             Property.Sensor(label="Sensor"),
             Property.Select(label="AutoMode",options=["Yes","No"], description="Switch Fermenterlogic automatically on and off -> Yes")])
class FermenterStep(CBPiFermentationStep):

    @action("Start Timer", [])
    async def start_timer(self):
        if self.timer.is_running is not True:
            self.cbpi.notify(self.name, 'Timer started', NotificationType.INFO)
            self.timer.start()
            self.timer.is_running = True
        else:
            self.cbpi.notify(self.name, 'Timer is already running', NotificationType.WARNING)

    @action("Add 5 Minutes to Timer", [])
    async def add_timer(self):
        if self.timer.is_running == True:
            self.cbpi.notify(self.name, '5 Minutes added', NotificationType.INFO)
            await self.timer.add(300)       
        else:
            self.cbpi.notify(self.name, 'Timer must be running to add time', NotificationType.WARNING)


    async def on_timer_done(self,timer):
        self.summary = ""
        self.fermenter.target_temp = 0
        if self.AutoMode == True:
            await self.setAutoMode(False)
        self.cbpi.notify(self.name, 'Step finished', NotificationType.SUCCESS)
       
        await self.next()

    async def on_timer_update(self,timer, seconds):
        self.summary = Timer.format_time(seconds)
        await self.push_update()

    async def on_start(self):
        logging.info(self.fermenter)
        self.AutoMode = True if self.props.get("AutoMode", "No") == "Yes" else False
        self.starttemp= self.get_sensor_value(self.props.get("Sensor", None)).get("value")    
        if self.fermenter is not None:
            self.fermenter.target_temp = int(self.props.get("Temp", 0))
        if self.AutoMode == True:
            await self.setAutoMode(True)
        await self.push_update()

        if self.fermenter is not None and self.timer is None:
            self.timer = Timer(int(self.props.get("Timer",0)) *60 ,on_update=self.on_timer_update, on_done=self.on_timer_done)
        elif self.fermenter is not None:
            try:
                if self.timer.is_running == True:
                    self.timer.start()
            except:
                pass

        self.summary = "Waiting for Target Temp"
        await self.push_update()

    async def on_stop(self):
        await self.timer.stop()
        self.summary = ""
        if self.AutoMode == True:
            await self.setAutoMode(False)
        await self.push_update()

    async def reset(self):
        self.timer = Timer(int(self.props.get("Timer",0)) *60 ,on_update=self.on_timer_update, on_done=self.on_timer_done)

    async def run(self):
        if self.fermenter.target_temp >= self.starttemp:
            while self.running == True:
                await asyncio.sleep(1)
                sensor_value = self.get_sensor_value(self.props.get("Sensor", None)).get("value")
                if sensor_value >= int(self.props.get("Temp",0)) and self.timer.is_running is not True:
                    self.timer.start()
                    self.timer.is_running = True
                    estimated_completion_time = datetime.fromtimestamp(time.time()+ (int(self.props.get("Timer",0)))*60)
                    self.cbpi.notify(self.name, 'Timer started. Estimated completion: {}'.format(estimated_completion_time.strftime("%H:%M")), NotificationType.INFO)
        else:
            while self.running == True:
                await asyncio.sleep(1)
                sensor_value = self.get_sensor_value(self.props.get("Sensor", None)).get("value")
                if sensor_value <= int(self.props.get("Temp",0)) and self.timer.is_running is not True:
                    self.timer.start()
                    self.timer.is_running = True
                    estimated_completion_time = datetime.fromtimestamp(time.time()+ (int(self.props.get("Timer",0)))*60)
                    self.cbpi.notify(self.name, 'Timer started. Estimated completion: {}'.format(estimated_completion_time.strftime("%H:%M")), NotificationType.INFO)

        return StepResult.DONE

    async def setAutoMode(self, auto_state):
        try:
            if (self.fermenter.instance is None or self.fermenter.instance.state == False) and (auto_state is True):
                await self.fermenter.instance.toggle(self.fermenter.id)
            elif (self.fermenter.instance.state == True) and (auto_state is False):
                await self.fermenter.instance.stop(self.fermenter.id)
            await self.push_update()

        except Exception as e:
            logging.error("Failed to switch on FermenterLogic {} {}".format(self.fermenter.id, e))


def setup(cbpi):
    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server

    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("FermenterNotificationStep", FermenterNotificationStep)
    cbpi.plugin.register("FermenterTargetTempStep", FermenterTargetTempStep)
    cbpi.plugin.register("FermenterStep", FermenterStep)
