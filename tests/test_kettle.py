import asyncio
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from core.craftbeerpi import CraftBeerPi


class KettleTestCase(AioHTTPTestCase):


    async def get_application(self):
        self.cbpi = CraftBeerPi()
        await self.cbpi.init_serivces()
        return self.cbpi.app

    @unittest_run_loop
    async def test_get(self):

        resp = await self.client.request("GET", "/kettle")
        assert resp.status == 200
        print(await resp.json())

    @unittest_run_loop
    async def test_crud(self):
        data = {
            "name": "Test",
            "sensor": None,
            "heater": "1",
            "automatic": None,
            "logic": "CustomKettleLogic",
            "config": {
                "test": "WOOHO"
            },
            "agitator": None,
            "target_temp": None
        }

        # Add new sensor
        resp = await self.client.post(path="/kettle/", json=data)
        assert resp.status == 200

        m = await resp.json()
        sensor_id = m["id"]

        # Get sensor
        resp = await self.client.get(path="/kettle/%s" % sensor_id)
        assert resp.status == 200

        m2 = await resp.json()
        sensor_id = m2["id"]

        # Update Sensor
        resp = await self.client.put(path="/kettle/%s" % sensor_id, json=m)
        assert resp.status == 200

        # # Delete Sensor
        resp = await self.client.delete(path="/kettle/%s" % sensor_id)
        assert resp.status == 204


