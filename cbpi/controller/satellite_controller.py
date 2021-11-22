

import asyncio
import json
from re import M
from asyncio_mqtt import Client, MqttError, Will, client
from contextlib import AsyncExitStack, asynccontextmanager
from cbpi import __version__
import logging


class SatelliteController:

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.logger = logging.getLogger(__name__)
        self.host = cbpi.static_config.get("mqtt_host", "localhost")
        self.port = cbpi.static_config.get("mqtt_port", 1883)
        self.username = cbpi.static_config.get("mqtt_username", None)
        self.password = cbpi.static_config.get("mqtt_password", None)
        self.client = None
        self.topic_filters = [
            ("cbpi/actor/+/on", self._actor_on),
            ("cbpi/actor/+/off", self._actor_off),
            ("cbpi/actor/+/power", self._actor_power),
        ]
        self.tasks = set()

    async def init(self):
        asyncio.create_task(self.init_client(self.cbpi))

    async def publish(self, topic, message, retain=False):
        if self.client is not None and self.client._connected:
            try:
                await self.client.publish(topic, message, qos=1, retain=retain)
            except:
                self.logger.warning("Failed to push data via mqtt")

    async def _actor_on(self, messages):
        async for message in messages:
            try:
                topic_key = message.topic.split("/")
                await self.cbpi.actor.on(topic_key[2])
            except:
                self.logger.warning("Failed to process actor on via mqtt")

    async def _actor_off(self, messages):
        async for message in messages:
            try:
                topic_key = message.topic.split("/")
                await self.cbpi.actor.off(topic_key[2])
            except:
                self.logger.warning("Failed to process actor off via mqtt")

    async def _actor_power(self, messages):
        async for message in messages:
            try:
                topic_key = message.topic.split("/")
                try:
                    power=int(message.payload.decode())
                    if power > 100: 
                        power = 100
                    if power < 0:
                        power = 0
                    await self.cbpi.actor.set_power(topic_key[2],power)
                    await self.cbpi.actor.actor_update(topic_key[2],power)
                except:
                    self.logger.warning("Failed to set actor power via mqtt. No valid power in message")
            except:
                self.logger.warning("Failed to set actor power via mqtt")

    def subcribe(self, topic, method):
        task = asyncio.create_task(self._subcribe(topic, method))
        return task

    async def _subcribe(self, topic, method):
        while True:
            try:
                if self.client._connected.done():
                    async with self.client.filtered_messages(topic) as messages:
                        await self.client.subscribe(topic)
                        async for message in messages:
                            await method(message.payload.decode())
            except asyncio.CancelledError as e:
                # Cancel
                self.logger.warning(
                    "Sub CancelledError Exception: {}".format(e))
                return
            except MqttError as e:
                self.logger.error("Sub MQTT Exception: {}".format(e))
            except Exception as e:
                self.logger.error("Sub Exception: {}".format(e))

            # wait before try to resubscribe
            await asyncio.sleep(5)

    async def init_client(self, cbpi):

        async def cancel_tasks(tasks):
            for task in tasks:
                if task.done():
                    continue
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        while True:
            try:
                async with AsyncExitStack() as stack:
                    self.tasks = set()
                    stack.push_async_callback(cancel_tasks, self.tasks)
                    self.client = Client(self.host, port=self.port, username=self.username, password=self.password, will=Will(topic="cbpi/diconnect", payload="CBPi Server Disconnected"))

                    await stack.enter_async_context(self.client)

                    for topic_filter in self.topic_filters:
                        topic = topic_filter[0]
                        method = topic_filter[1]
                        manager = self.client.filtered_messages(topic)
                        messages = await stack.enter_async_context(manager)
                        task = asyncio.create_task(method(messages))
                        self.tasks.add(task)

                    for topic_filter in self.topic_filters:
                        topic = topic_filter[0]
                        await self.client.subscribe(topic)

                    self.logger.info("MQTT Connected to {}:{}".format(self.host, self.port))
                    await asyncio.gather(*self.tasks)

            except MqttError as e:
                self.logger.error("MQTT Exception: {}".format(e))
            except Exception as e:
                self.logger.error("MQTT General Exception: {}".format(e))
            await asyncio.sleep(5)
