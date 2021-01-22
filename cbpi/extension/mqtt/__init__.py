import json

from cbpi.utils.encoder import ComplexEncoder
from hbmqtt.mqtt.constants import QOS_0
from hbmqtt.client import MQTTClient

class CBPiMqttClient:

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.cbpi.bus.register("#", self.listen)
        self.client = None
        self.cbpi.app.on_startup.append(self.init_client)


    async def init_client(self, cbpi):

        self.client = MQTTClient()
        await self.client.connect('mqtt://localhost:1883')


    async def listen(self, topic, **kwargs):
        if self.client is not None:
            await self.client.publish(topic, str.encode(json.dumps(kwargs, cls=ComplexEncoder)), QOS_0)

def setup(cbpi):
    '''
    This method is called by the server during startup
    Here you need to register your plugins at the server

    :param cbpi: the cbpi core
    :return:
    '''
    print("MQTT")
    print("###################")
    print("###################")
    print("###################")
    print("###################")
    client = CBPiMqttClient(cbpi)

