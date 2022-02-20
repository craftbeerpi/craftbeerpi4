from aiohttp.test_utils import unittest_run_loop
from tests.cbpi_config_fixture import CraftBeerPiTestCase


class KettleTestCase(CraftBeerPiTestCase):

    @unittest_run_loop
    async def test_get(self):

        resp = await self.client.request("GET", "/kettle")
        assert resp.status == 200
        kettle = resp.json()
        assert kettle != None

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

        kettle_id = m["id"]
        print("KETTLE", m["id"], m)
 
        # Update Kettle
        resp = await self.client.put(path="/kettle/%s" % kettle_id, json=m)
        assert resp.status == 200

        # Set Kettle target temp
        resp = await self.client.post(path="/kettle/%s/target_temp" % kettle_id, json={"temp":75})
        assert resp.status == 204

        # # Delete Sensor
        resp = await self.client.delete(path="/kettle/%s" % kettle_id)
        assert resp.status == 204




