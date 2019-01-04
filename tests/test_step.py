import asyncio
from unittest import mock

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from core.craftbeerpi import CraftBeerPi


class StepTestCase(AioHTTPTestCase):


    async def get_application(self):
        self.cbpi = CraftBeerPi()
        await self.cbpi.init_serivces()
        return self.cbpi.app

    @unittest_run_loop
    async def test_get(self):

        resp = await self.client.request("GET", "/step")
        assert resp.status == 200

        resp = await self.client.request("GET", "/step/types")
        assert resp.status == 200


    @unittest_run_loop
    async def test_crud(self):
        data = {
            "name": "Test",
            "type": "CustomStepCBPi",
        }

        # Add new sensor
        resp = await self.client.post(path="/step/", json=data)
        assert resp.status == 200

        m = await resp.json()
        print(m)
        sensor_id = m["id"]

        # Get sensor
        resp = await self.client.get(path="/step/%s" % sensor_id)
        assert resp.status == 200

        m2 = await resp.json()
        sensor_id = m2["id"]

        # Update Sensor
        resp = await self.client.put(path="/step/%s" % sensor_id, json=m)
        assert resp.status == 200

        # # Delete Sensor
        resp = await self.client.delete(path="/step/%s" % sensor_id)
        assert resp.status == 204

    def create_wait_callback(self, topic):
        future = self.cbpi.app.loop.create_future()

        async def test(**kwargs):
            print("GOON")
            future.set_result("OK")
        self.cbpi.bus.register(topic, test, once=True)
        return future

    async def wait(self, future):
        done, pending = await asyncio.wait({future})

        if future in done:
            pass

    @unittest_run_loop
    async def test_process(self):
        await self.cbpi.step.stop()

        with mock.patch.object(self.cbpi.step, 'start', wraps=self.cbpi.step.start) as mock_obj:

            future = self.create_wait_callback("step/+/started")
            await self.cbpi.step.start()
            await self.wait(future)

            future = self.create_wait_callback("step/+/started")
            await self.cbpi.step.next()
            await self.wait(future)

            future = self.create_wait_callback("step/+/started")
            await self.cbpi.step.next()
            await self.wait(future)

            future = self.create_wait_callback("step/+/started")
            await self.cbpi.step.next()
            await self.wait(future)

            future = self.create_wait_callback("job/step/done")
            await self.cbpi.step.stop()
            await self.wait(future)
            print("COUNT", mock_obj.call_count)
            print("ARGS", mock_obj.call_args_list)

