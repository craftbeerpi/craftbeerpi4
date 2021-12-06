from cbpi.api import parameters, Property
from . import MQTTActor

@parameters([
    Property.Text(label="Topic", configurable=True, description = "MQTT Topic"),
    Property.Text(label="Payload", configurable=True, description = "Payload that is sent as MQTT message. Available placeholders are {switch_onoff}: [on|off], {switch_10}: [1|0], {power}: [0-100].")
])
class GenericMqttActor(MQTTActor):
    def __init__(self, cbpi, id, props):
        MQTTActor.__init__(self, cbpi, id, props)
        self.payload = ""

    async def on_start(self):
         await MQTTActor.on_start(self)
         self.payload = self.props.get("Payload", "{{\"state\": \"{switch_onoff}\", \"power\": {power}}}")

    def normalize_power_value(self, power):
        if power is not None:
            if power != self.power:
                power = min(100, power)
                power = max(0, power)
                self.power = round(power)
    
    async def publish_mqtt_message(self, topic, payload):
        self.logger.info("Publish '{payload}' to '{topic}'".format(payload = payload, topic = self.topic))
        await self.cbpi.satellite.publish(self.topic, payload, True)

    async def on(self, power=None):
        self.normalize_power_value(power)
        formatted_payload = self.payload.format(switch_onoff = "on", switch_10 = 1, power = self.power)
        await self.publish_mqtt_message(self.topic, formatted_payload)
        self.state = True

    async def off(self):
        formatted_payload = self.payload.format(switch_onoff = "off", switch_10 = 0, power = self.power)
        await self.publish_mqtt_message(self.topic, formatted_payload)
        self.state = False