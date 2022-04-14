from aiohttp.test_utils import unittest_run_loop
from tests.cbpi_config_fixture import CraftBeerPiTestCase


class IndexTestCase(CraftBeerPiTestCase):

    @unittest_run_loop
    async def test_index(self):


        # Test Index Page
        resp = await self.client.get(path="/")
        assert resp.status == 200

    @unittest_run_loop
    async def test_404(self):
        # Test Index Page
        resp = await self.client.get(path="/abc")
        assert resp.status == 500

    @unittest_run_loop
    async def test_wrong_login(self):
        resp = await self.client.post(path="/login", data={"username": "beer", "password": "123"})
        print("REPONSE STATUS", resp.status)
        assert resp.status == 403

    @unittest_run_loop
    async def test_login(self):

        resp = await self.client.post(path="/login", data={"username": "cbpi", "password": "123"})
        print("REPONSE STATUS", resp.status)
        assert resp.status == 200

        resp = await self.client.get(path="/logout")
        print("REPONSE STATUS LGOUT", resp.status)
        assert resp.status == 200
