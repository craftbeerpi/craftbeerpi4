from aiohttp.test_utils import unittest_run_loop
from tests.cbpi_config_fixture import CraftBeerPiTestCase

from cbpi.craftbeerpi import CraftBeerPi


class DashboardTestCase(CraftBeerPiTestCase):

    @unittest_run_loop
    async def test_crud(self):
        data = {
            "name": "MyDashboard",

        }

        dashboard_content = {
            "type": "Test",
            "x": 0,
            "y": 0,
            "config": {}
        }

        resp = await self.client.get(path="/dashboard/current")
        assert resp.status == 200

        dashboard_id = await resp.json()

         # Add dashboard content
        dashboard_content["dbid"] = dashboard_id
        resp = await self.client.post(path="/dashboard/%s/content" % dashboard_id, json=dashboard_content)
        assert resp.status == 204