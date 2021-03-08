import asyncio
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from cbpi.craftbeerpi import CraftBeerPi


class SensorTestCase(AioHTTPTestCase):

    async def get_application(self):
        self.cbpi = CraftBeerPi()
        await self.cbpi.init_serivces()
        return self.cbpi.app

    @unittest_run_loop
    async def test_crud(self):

        data = {
            "name": "CustomSensor",
            "type": "CustomSensor",
            "config": {
                "interval": 1
            }
        }

        # Add new sensor
        resp = await self.client.post(path="/sensor/", json=data)
        assert resp.status == 200

        m = await resp.json()
        sensor_id = m["id"]

        # Get sensor
        resp = await self.client.get(path="/sensor/%s"% sensor_id)
        assert resp.status == 200

        m2 = await resp.json()
        sensor_id = m2["id"]

        # Update Sensor
        resp = await self.client.put(path="/sensor/%s"  % sensor_id, json=m)
        assert resp.status == 200

        # # Delete Sensor
        resp = await self.client.delete(path="/sensor/%s" % sensor_id)
        assert resp.status == 204
