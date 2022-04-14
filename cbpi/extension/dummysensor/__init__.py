# -*- coding: utf-8 -*-
import asyncio
import random
import logging
from cbpi.api import *
from cbpi.api.base import CBPiBase
from cbpi.api.dataclasses import Kettle, Props, Fermenter

@parameters([])
class CustomSensor(CBPiSensor):

    def __init__(self, cbpi, id, props):
        super(CustomSensor, self).__init__(cbpi, id, props)
        self.value = 0

    async def run(self):
        while self.running:
            self.value = random.randint(10, 100)
            self.log_data(self.value)

            self.push_update(self.value)
            await asyncio.sleep(1)

    def get_state(self):
        return dict(value=self.value)

@parameters([Property.Number(label="Pressure", configurable=True, description="Start Pressure"),
             Property.Number(label="PressureIncrease", configurable=True, description="Pressure increase per hour"),
             Property.Number(label="PressureDecrease", configurable=True, description="Pressure decrease per second on openm valve"),
             Property.Fermenter(label="Fermenter",description="Fermenter")])
class DummyPressure(CBPiSensor):

    def __init__(self, cbpi, id, props):
        super(DummyPressure, self).__init__(cbpi, id, props)
        self.value = float(self.props.get("Pressure",0))
        fermenter=self.props.get("Fermenter",None)
        self.fermenter=self.get_fermenter(fermenter)
        self.valve=self.fermenter.valve

    async def run(self):
        self.uprate=float(self.props.get("PressureIncrease",0))/3600
        self.decrease=float(self.props.get("PressureDecrease",0))
        logging.info(self.uprate)
        logging.info(self.decrease)

        while self.running:
            valve_state=self.get_actor_state(self.valve)
            fermenter_instance=self.fermenter.instance
            if fermenter_instance:
                fermenter_state=fermenter_instance.state
            else:
                fermenter_state = False
            if valve_state == False and fermenter_state:
                self.value = self.value + self.uprate
            elif valve_state and fermenter_state:
                self.value=self.value-self.decrease

            self.log_data(self.value)

            self.push_update(round(self.value,2))
            await asyncio.sleep(1)

    def get_state(self):
        return dict(value=self.value)

def setup(cbpi):
    '''
    This method is called by the server during startup
    Here you need to register your plugins at the server

    :param cbpi: the cbpi core
    :return:
    '''
    cbpi.plugin.register("CustomSensor", CustomSensor)
    cbpi.plugin.register("DummyPressure", DummyPressure)
