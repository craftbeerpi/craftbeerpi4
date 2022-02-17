import time

import aiosqlite
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from cbpi.api.config import ConfigType

from cbpi.craftbeerpi import CraftBeerPi


class ConfigTestCase(AioHTTPTestCase):


    async def get_application(self):
        self.cbpi = CraftBeerPi()
        await self.cbpi.init_serivces()
        return self.cbpi.app


    @unittest_run_loop
    async def test_get(self):

        assert self.cbpi.config.get("CBPI_TEST_1", 1) == "22"

    @unittest_run_loop
    async def test_set_get(self):
        value = str(time.time())

        await self.cbpi.config.set("CBPI_TEST_2", value)

        assert self.cbpi.config.get("CBPI_TEST_2", 1) == value

    @unittest_run_loop
    async def test_http_set(self):
        value = str(time.time())
        key = "CBPI_TEST_3"
        await self.cbpi.config.set(key, value)
        assert self.cbpi.config.get(key, 1) == value

        resp = await self.client.request("PUT", "/config/%s/" % key, json={'value': '1'})
        assert resp.status == 204
        assert self.cbpi.config.get(key, -1) == "1"

    @unittest_run_loop
    async def test_http_get(self):
        resp = await self.client.request("GET", "/config/")
        assert resp.status == 200

    @unittest_run_loop
    async def test_get_default(self):
        value = self.cbpi.config.get("HELLO_WORLD", None)
        assert value == None