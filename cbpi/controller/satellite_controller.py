import asyncio

from asyncio_mqtt import Client, MqttError, Will
from contextlib import AsyncExitStack, asynccontextmanager


class SatelliteController:
    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.client = None

    async def init(self):
        asyncio.create_task(self.init_client(self.cbpi))

    async def publish(self, topic, message):
        print("MQTT ON")
        await self.client.publish(topic, message, qos=1)

    async def handle_message(self, messages):
        async for message in messages:
            print("FILTERED", message.payload.decode())

    async def handle_unfilterd_message(self, messages):
        async for message in messages:
            print("UNFILTERED", message.payload.decode())

    async def init_client(self, cbpi):
        async def log_messages(messages, template):

            async for message in messages:
                print(template.format(message.payload.decode()))

        async def cancel_tasks(tasks):
            for task in tasks:
                if task.done():
                    continue
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        async with AsyncExitStack() as stack:

            tasks = set()
            stack.push_async_callback(cancel_tasks, tasks)

            self.client = Client(
                "localhost",
                will=Will(topic="cbpi/diconnect", payload="CBPi Server Disconnected"),
            )
            await stack.enter_async_context(self.client)

            topic_filters = ("cbpi/sensor/#", "cbpi/actor/#")
            for topic_filter in topic_filters:
                # Log all messages that matches the filter
                manager = self.client.filtered_messages(topic_filter)
                messages = await stack.enter_async_context(manager)
                task = asyncio.create_task(self.handle_message(messages))
                tasks.add(task)

            messages = await stack.enter_async_context(
                self.client.unfiltered_messages()
            )
            task = asyncio.create_task(self.handle_unfilterd_message(messages))
            tasks.add(task)

            await self.client.subscribe("cbpi/#")
            await asyncio.gather(*tasks)
