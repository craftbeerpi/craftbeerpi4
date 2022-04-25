import asyncio
from aiohttp.test_utils import unittest_run_loop
from tests.cbpi_config_fixture import CraftBeerPiTestCase

class StepTestCase(CraftBeerPiTestCase):

    @unittest_run_loop
    async def test_get(self):

        resp = await self.client.request("GET", "/step2")
        print(resp)
        assert resp.status == 200


    @unittest_run_loop
    async def test_crud(self):
        data = {
            "name": "Test",
            "type": "CustomStepCBPi",
            "config": {}
        }

        # Add new step
        resp = await self.client.post(path="/step2/", json=data)
        assert resp.status == 200

        m = await resp.json()
        print("Step", m)
        sensor_id = m["id"]

         # Update step
        resp = await self.client.put(path="/step2/%s" % sensor_id, json=m)
        assert resp.status == 200

        # # Delete step
        resp = await self.client.delete(path="/step2/%s" % sensor_id)
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