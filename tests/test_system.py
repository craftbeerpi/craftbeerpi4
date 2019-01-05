from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from cbpi.craftbeerpi import CraftBeerPi


class IndexTestCase(AioHTTPTestCase):

    async def get_application(self):
        self.cbpi = CraftBeerPi()
        await self.cbpi.init_serivces()
        return self.cbpi.app

    @unittest_run_loop
    async def test_endpoints(self):


        # Test Index Page
        resp = await self.client.post(path="/system/restart")
        assert resp.status == 200

        resp = await self.client.post(path="/system/shutdown")
        assert resp.status == 200

        resp = await self.client.get(path="/system/jobs")
        assert resp.status == 200

        resp = await self.client.get(path="/system/events")
        assert resp.status == 200

