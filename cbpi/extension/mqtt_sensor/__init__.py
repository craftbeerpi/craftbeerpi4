# -*- coding: utf-8 -*-
import asyncio
from cbpi.api.dataclasses import NotificationAction, NotificationType
from cbpi.api import parameters, Property, CBPiSensor
from cbpi.api import *
import logging
import json
import time
from datetime import datetime

@parameters([Property.Text(label="Topic", configurable=True, description="MQTT Topic"),
             Property.Text(label="PayloadDictionary", configurable=True, default_value="",
                           description="Where to find msg in payload, leave blank for raw payload"),
             Property.Kettle(label="Kettle", description="Reduced logging if Kettle is inactive (only Kettle or Fermenter to be selected)"),
             Property.Fermenter(label="Fermenter", description="Reduced logging in seconds if Fermenter is inactive (only Kettle or Fermenter to be selected)"),
             Property.Number(label="ReducedLogging", configurable=True, description="Reduced logging frequency in seconds if selected Kettle or Fermenter is inactive (default is 60 sec)"),
             Property.Number(label="Timeout", configurable=True, unit="sec",
                            description="Timeout in seconds to send notification (default:60 | deactivated: 0)")])
class MQTTSensor(CBPiSensor):

    def __init__(self, cbpi, id, props):
        super(MQTTSensor, self).__init__(cbpi, id, props)
        self.Topic = self.props.get("Topic", None)
        self.payload_text = self.props.get("PayloadDictionary", None)
        if self.payload_text != None:
            self.payload_text = self.payload_text.split('.')
        self.mqtt_task = self.cbpi.satellite.subcribe(self.Topic, self.on_message)
        self.value: float = 999
        self.timeout=int(self.props.get("Timeout", 60))
        self.starttime = time.time()
        self.notificationsend = False
        self.nextchecktime=self.starttime+self.timeout
        self.lastdata=time.time()
        self.lastlog=0
        self.sensor=self.get_sensor(self.id)
        self.reducedfrequency=int(self.props.get("ReducedLogging", 60))
        self.kettleid=self.props.get("Kettle", None)
        self.fermenterid=self.props.get("Fermenter", None)
        self.reducedlogging = True if self.kettleid or self.fermenterid else False

        if self.kettleid is not None and self.fermenterid is not None:
            self.reducedlogging=False
            self.cbpi.notify("MQTTSensor", "Sensor '" + str(self.sensor.name) + "' cant't have Fermenter and Kettle defined for reduced logging.", NotificationType.WARNING, action=[NotificationAction("OK", self.Confirm)])
            
    async def Confirm(self, **kwargs):
        self.nextchecktime = time.time() + self.timeout
        self.notificationsend = False
        pass

    async def message(self):
        target_timestring= datetime.fromtimestamp(self.lastdata)
        self.cbpi.notify("MQTTSensor Timeout", "Sensor '" + str(self.sensor.name) + "' did not respond. Last data received: "+target_timestring.strftime("%D %H:%M"), NotificationType.WARNING, action=[NotificationAction("OK", self.Confirm)])
        pass

    async def on_message(self, message):
        val = json.loads(message)
        try:
            if self.payload_text is not None:
                for key in self.payload_text:
                    val = val.get(key, None)

            if isinstance(val, (int, float, str)):
                self.value = float(val)
                self.push_update(self.value)
                if self.reducedlogging == True:
                    await self.logvalue()
                else:
                    logging.info("MQTTSensor {} regular logging".format(self.sensor.name))
                    self.log_data(self.value)
                    self.lastlog = time.time()

                if self.timeout !=0:
                    self.nextchecktime = time.time() + self.timeout
                    self.notificationsend = False
                    self.lastdata=time.time()
        except Exception as e:
            logging.error("MQTT Sensor Error {}".format(e))

    async def logvalue(self):
        self.kettle = self.get_kettle(self.kettleid) if self.kettleid is not None else None 
        self.fermenter = self.get_fermenter(self.fermenterid) if self.fermenterid is not None else None
        now=time.time()            
        if self.kettle is not None:
            try:
                kettlestatus=self.kettle.instance.state
            except:
                kettlestatus=False
            if kettlestatus:
                self.log_data(self.value)
                logging.info("MQTTSensor {} Kettle Active".format(self.sensor.name))
                self.lastlog = time.time()
            else:
                logging.info("MQTTSensor {} Kettle Inactive".format(self.sensor.name))
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
                logging.info("MQTTSensor {} Fermenter Active".format(self.sensor.name))
                self.lastlog = time.time()
            else:
                logging.info("MQTTSensor {} Fermenter Inactive".format(self.sensor.name))
                if now >= self.lastlog + self.reducedfrequency:
                    self.log_data(self.value)
                    self.lastlog = time.time()
                    logging.info("Logged with reduced freqency")
                    pass            

    async def run(self):
        while self.running:
            if self.timeout !=0:         
                if time.time() > self.nextchecktime and self.notificationsend == False:   
                    await self.message()
                    self.notificationsend=True
            await asyncio.sleep(1)

    def get_state(self):
        return dict(value=self.value)

    async def on_stop(self):
        if not self.mqtt_task.done():
            logging.warning("Task not done -> cancelling")
            self.mqtt_task.cancel()
        try:            
            logging.warning("trying to call cancelled task")
            await self.mqtt_task
        except asyncio.CancelledError:
            logging.warning("Task has been Cancelled")
            pass


def setup(cbpi):
    '''
    This method is called by the server during startup
    Here you need to register your plugins at the server

    :param cbpi: the cbpi core
    :return:
    '''
    if str(cbpi.static_config.get("mqtt", False)).lower() == "true":
        cbpi.plugin.register("MQTTSensor", MQTTSensor)
