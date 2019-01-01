import aiohttp
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from core.craftbeerpi import CraftBeerPi


class MyAppTestCase(AioHTTPTestCase):




    async def get_application(self):
        self.cbpi = CraftBeerPi()
        await self.cbpi.init_serivces()
        return self.cbpi.app


    @unittest_run_loop
    async def test_example(self):

        resp = await self.client.post(path="/login", data={"username": "cbpi", "password": "123"})
        assert resp.status == 200

        resp = await self.client.request("GET", "/actor/1/on")
        assert resp.status == 204
        i = await self.cbpi.actor.get_one(1)
        assert i.instance.state is True

        resp = await self.client.request("GET", "/actor/1/off")
        assert resp.status == 204
        i = await self.cbpi.actor.get_one(1)
        assert i.instance.state is False

        resp = await self.client.request("GET", "/actor/1/toggle")

        assert resp.status == 204
        i = await self.cbpi.actor.get_one(1)
        assert i.instance.state is True

        resp = await self.client.request("GET", "/actor/1/toggle")
        assert resp.status == 204
        i = await self.cbpi.actor.get_one(1)
        assert i.instance.state is False



