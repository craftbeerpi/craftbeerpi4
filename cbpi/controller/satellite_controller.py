
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
        self.kettlecontroller = cbpi.kettle
        self.fermentercontroller = cbpi.fermenter
        self.sensorcontroller = cbpi.sensor
        self.actorcontroller = cbpi.actor
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
            ("cbpi/updateactor", self._actorupdate),
            ("cbpi/updatekettle", self._kettleupdate),
            ("cbpi/updatesensor", self._sensorupdate),
            ("cbpi/updatefermenter", self._fermenterupdate),
        
        ]
        self.tasks = set()

    async def init(self):
        asyncio.create_task(self.init_client(self.cbpi))

    async def publish(self, topic, message, retain=False):
        if self.client is not None and self.client._connected:
            try:
                await self.client.publish(topic, message, qos=1, retain=retain)
            except Exception as e:
                self.logger.warning("Failed to push data via mqtt: {}".format(e))

    async def _actor_on(self, messages):
        async for message in messages:
            try:
                topic_key = message.topic.split("/")
                await self.cbpi.actor.on(topic_key[2])
            except Exception as e:
                self.logger.warning("Failed to process actor on via mqtt: {}".format(e))

    async def _actor_off(self, messages):
        async for message in messages:
            try:
                topic_key = message.topic.split("/")
                await self.cbpi.actor.off(topic_key[2])
            except Exception as e:
                self.logger.warning("Failed to process actor off via mqtt: {}".format(e))

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
                    #await self.cbpi.actor.actor_update(topic_key[2],power)
                except:
                    self.logger.warning("Failed to set actor power via mqtt. No valid power in message")
            except:
                self.logger.warning("Failed to set actor power via mqtt")

    async def _kettleupdate(self, messages):
        async for message in messages:
            try:
                self.kettle=self.kettlecontroller.get_state()
                for item in self.kettle['data']:
                    self.cbpi.push_update("cbpi/{}/{}".format("kettleupdate",item['id']), item)
            except Exception as e:
                self.logger.warning("Failed to send kettleupdate via mqtt: {}".format(e))

    async def _fermenterupdate(self, messages):
        async for message in messages:
            try:
                self.fermenter=self.fermentercontroller.get_state()
                for item in self.fermenter['data']:
                    self.cbpi.push_update("cbpi/{}/{}".format("fermenterupdate",item['id']), item)
            except Exception as e:
                self.logger.warning("Failed to send fermenterupdate via mqtt: {}".format(e))

    async def _actorupdate(self, messages):
        async for message in messages:
            try:
                self.actor=self.actorcontroller.get_state()
                for item in self.actor['data']:
                    self.cbpi.push_update("cbpi/{}/{}".format("actorupdate",item['id']), item)
            except Exception as e:
                self.logger.warning("Failed to send actorupdate via mqtt: {}".format(e))

    async def _sensorupdate(self, messages):
        async for message in messages:
            try:
                self.sensor=self.sensorcontroller.get_state()
                for item in self.sensor['data']:
                    self.cbpi.push_update("cbpi/{}/{}".format("sensorupdate",item['id']), item)
            except Exception as e:
                self.logger.warning("Failed to send sensorupdate via mqtt: {}".format(e))

    def subcribe(self, topic, method):
        task = asyncio.create_task(self._subcribe(topic, method))
        return task

    async def _subcribe(self, topic, method):
        while True:
            try:
                if self.client._connected.done():
                    async with self.client.messages() as messages:
                        await self.client.subscribe(topic)
                        async for message in messages:
                            if message.topic.matches(topic):
                                await method(message.payload.decode())
            except asyncio.CancelledError:
                # Cancel
                self.logger.warning("Sub Cancelled")
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

        # This part needs to be updated in future as filtered_messages() is depracted and will be removed in future from asyncio-mqtt
        while True:

            try:
                async with AsyncExitStack() as stack:
                    self.tasks = set()
                    stack.push_async_callback(cancel_tasks, self.tasks)
                    self.client = Client(self.host, port=self.port, username=self.username, password=self.password, will=Will(topic="cbpi/disconnect", payload="CBPi Server Disconnected"))

                    await stack.enter_async_context(self.client)

                    for topic_filter in self.topic_filters:
                        topic = topic_filter[0]
                        logging.info("Topic: "+topic)
                        method = topic_filter[1]
                        logging.info("Method: "+str(method))
                        manager = self.client.filtered_messages(topic)
                        logging.info("Manager: " +str(manager))
                        messages = await stack.enter_async_context(manager)
                        logging.info("Messages: " +str(messages))
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
