# -*- coding: utf-8 -*-
import asyncio
from cbpi.api.dataclasses import NotificationAction, NotificationType
from cbpi.api import parameters, Property, CBPiSensor
from cbpi.api import *
import logging
import json
import time

@parameters([Property.Text(label="Topic", configurable=True, description="MQTT Topic"),
             Property.Text(label="PayloadDictionary", configurable=True, default_value="",
                           description="Where to find msg in payload, leave blank for raw payload"),
             Property.Number(label="Timeout", configurable="True",unit="sec",
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

    async def Confirm(self, **kwargs):
        self.nextchecktime = time.time() + self.timeout
        self.notificationsend = False
        pass

    async def message(self):
        self.cbpi.notify("MQTTSensor Timeout", "Sensor " + str(self.Topic) + " did not respond", NotificationType.WARNING, action=[NotificationAction("OK", self.Confirm)])
        pass

    async def on_message(self, message):
        val = json.loads(message)
        try:
            if self.payload_text is not None:
                for key in self.payload_text:
                    val = val.get(key, None)

            if isinstance(val, (int, float, str)):
                self.value = float(val)
                self.log_data(self.value)
                self.push_update(self.value)
                if self.timeout !=0:
                    self.nextchecktime = time.time() + self.timeout
                    self.notificationsend = False
        except Exception as e:
            logging.info("MQTT Sensor Error {}".format(e))

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
        if self.mqtt_task.done() is False:
            self.mqtt_task.cancel()
            try:
                await self.mqtt_task
            except asyncio.CancelledError:
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
