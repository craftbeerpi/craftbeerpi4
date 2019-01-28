import asyncio
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from cbpi.craftbeerpi import CraftBeerPi


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
    async def test_heater(self):
        resp = await self.client.get("/kettle/1/heater/on")
        assert resp.status == 204

        resp = await self.client.get("/kettle/1/heater/off")
        assert resp.status == 204

    @unittest_run_loop
    async def test_agitator(self):
        resp = await self.client.get("/kettle/1/agitator/on")
        assert resp.status == 204

        resp = await self.client.get("/kettle/1/agitator/off")
        assert resp.status == 204

    @unittest_run_loop
    async def test_temp(self):
        resp = await self.client.get("/kettle/1/temp")
        assert resp.status == 204

        resp = await self.client.get("/kettle/1/targettemp")
        assert resp.status == 200

    @unittest_run_loop
    async def test_automatic(self):
        resp = await self.client.post("/kettle/1/automatic")
        assert resp.status == 204


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
        print(m)
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


