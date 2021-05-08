import json

from cbpi.utils.encoder import ComplexEncoder
from hbmqtt.mqtt.constants import QOS_0
from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_1, QOS_2
from asyncio_mqtt import Client, MqttError, Will
import asyncio


class CBPiMqttClient:
    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.cbpi.bus.register("#", self.listen)
        self.client = None
        self._loop = asyncio.get_event_loop()
        self._loop.create_task(self.init_client(self.cbpi))

    async def init_client(self, cbpi):

        async with Client(
            "localhost", will=Will(topic="cbpi/diconnect", payload="MY CLIENT")
        ) as client:
            async with client.filtered_messages("cbpi/#") as messages:
                await client.subscribe("cbpi/#")
                async for message in messages:
                    await self.cbpi.actor.on("YwGzXvWMpmbLb6XobesL8n")

    async def listen(self, topic, **kwargs):
        if self.client is not None:
            await self.client.publish(
                topic, str.encode(json.dumps(kwargs, cls=ComplexEncoder)), QOS_0
            )


def setup(cbpi):
    """
    This method is called by the server during startup
    Here you need to register your plugins at the server

    :param cbpi: the cbpi core
    :return:
    """

    client = CBPiMqttClient(cbpi)
