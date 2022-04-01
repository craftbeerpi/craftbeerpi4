from aiohttp.test_utils import unittest_run_loop
from tests.cbpi_config_fixture import CraftBeerPiTestCase


class IndexTestCase(CraftBeerPiTestCase):

    @unittest_run_loop
    async def test_endpoints(self):
        # Test Index Page
        resp = await self.client.post(path="/system/restart")
        assert resp.status == 200

        resp = await self.client.post(path="/system/shutdown")
        assert resp.status == 200

