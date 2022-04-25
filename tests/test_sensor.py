from aiohttp.test_utils import unittest_run_loop
from tests.cbpi_config_fixture import CraftBeerPiTestCase


class SensorTestCase(CraftBeerPiTestCase):

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

        # Get sensor value
        resp = await self.client.get(path="/sensor/%s"% sensor_id)
        assert resp.status == 200

        m2 = await resp.json()

        # Update Sensor
        resp = await self.client.put(path="/sensor/%s"  % sensor_id, json=m)
        assert resp.status == 200

        # # Delete Sensor
        resp = await self.client.delete(path="/sensor/%s" % sensor_id)
        assert resp.status == 204
