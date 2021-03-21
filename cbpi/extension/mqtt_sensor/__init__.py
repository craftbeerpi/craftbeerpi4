# -*- coding: utf-8 -*-
import asyncio

from cbpi.api import parameters, Property, CBPiSensor


@parameters([Property.Text(label="Topic", configurable=True)])
class MQTTSensor(CBPiSensor):

    async def on_message(self, message):
        try:
            self.value = float(message)
            self.log_data(self.value)
            self.push_update(self.value)
        except Exception as e:
            print(e)

    def __init__(self, cbpi, id, props):
        super(MQTTSensor, self).__init__(cbpi, id, props)
        self.mqtt_task = self.cbpi.satellite.subcribe(self.props.Topic, self.on_message)
        self.value: int = 0

    async def run(self):
        while self.running:
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
    if cbpi.static_config.get("mqtt", False) is True:
        cbpi.plugin.register("MQTTSensor", MQTTSensor)
