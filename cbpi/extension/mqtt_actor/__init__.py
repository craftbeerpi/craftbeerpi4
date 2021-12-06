# -*- coding: utf-8 -*-
from cbpi.api import *
from .mqtt_actor import MQTTActor
from .generic_mqtt_actor import GenericMqttActor
from .tasmota_mqtt_actor import TasmotaMqttActor

def setup(cbpi):
    '''
    This method is called by the server during startup
    Here you need to register your plugins at the server

    :param cbpi: the cbpi core
    :return:
    '''
    if str(cbpi.static_config.get("mqtt", False)).lower() == "true":
        cbpi.plugin.register("MQTTActor", MQTTActor)
        cbpi.plugin.register("MQTT Actor (Generic)", GenericMqttActor)
        cbpi.plugin.register("MQTT Actor (Tasmota)", TasmotaMqttActor)