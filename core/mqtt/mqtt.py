from aiojobs.aiohttp import get_scheduler_from_app
from hbmqtt.broker import Broker
from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_1, QOS_0
from typing import Callable

from core.mqtt_matcher import MQTTMatcher


class MQTT():
    def __init__(self,cbpi):

        self.config = {
            'listeners': {
                'default': {
                    'type': 'tcp',
                    'bind': '0.0.0.0:1885',
                },
                'ws': {
                    'bind': '0.0.0.0:8081',
                    'type': 'ws'
                }
            },
            'sys_interval': 10,
            'topic-check': {
                'enabled': True,
                'plugins': [
                    'topic_taboo'
                ]
            },
            'auth': {
                'allow-anonymous': True,
                'password-file': '/Users/manuelfritsch/github/aio_sample.cbpi/user.txt'
            }
        }

        self.cbpi = cbpi
        self.broker = Broker(self.config, plugin_namespace="hbmqtt.broker.plugins")
        self.client = MQTTClient()
        self.matcher = MQTTMatcher()
        self.mqtt_methods = {"test": self.ok_msg, "$SYS/broker/#": self.sysmsg}
        self.cbpi.app.on_startup.append(self.start_broker)
        self.count = 0

    def sysmsg(self, msg):

        print("SYS", msg)

    def ok_msg(self, msg):
        self.count = self.count + 1
        print("MSFG", msg, self.count)

    def publish(self, topic, message):
        print("PUSH NOW", topic)
        self.cbpi.app.loop.create_task(self.client.publish(topic, str.encode(message), QOS_0))

    def register_callback(self, func: Callable, topic) -> None:

        self.mqtt_methods[topic] = func

    async def on_message(self):
        while True:

            message = await self.client.deliver_message()
            matched = False
            packet = message.publish_packet
            print(message.topic)
            #print(message.topic.split('/'))
            data = packet.payload.data.decode("utf-8")

            for callback in self.matcher.iter_match(message.topic):
                print("MATCH")
                callback(data)
                matched = True

            if matched == False:
                print("NO HANDLER", data)

    async def start_broker(self, app):

        await self.broker.start()
        #
        await self.client.connect('mqtt://username:manuel@localhost:1885')
        # await self.client.connect('mqtt://broker.hivemq.com:1883')

        for k, v in self.mqtt_methods.items():
            print("############MQTT Subscribe:", k, v)
            await self.client.subscribe([(k, QOS_1)])
            self.matcher[k] = v
        await get_scheduler_from_app(app).spawn(self.on_message())
