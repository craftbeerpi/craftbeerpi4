import asyncio
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

    @unittest_run_loop
    async def test_process(self):
        resp = await self.client.request("GET", "/step/stop")
        assert resp.status == 204

        resp = await self.client.request("GET", "/step/start")
        assert resp.status == 204

        resp = await self.client.request("GET", "/step/next")
        assert resp.status == 204

        resp = await self.client.request("GET", "/step/stop")
        assert resp.status == 204




