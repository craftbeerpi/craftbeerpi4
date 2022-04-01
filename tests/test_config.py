import time

from aiohttp.test_utils import unittest_run_loop
from tests.cbpi_config_fixture import CraftBeerPiTestCase

class ConfigTestCase(CraftBeerPiTestCase):

    @unittest_run_loop
    async def test_get(self):

        assert self.cbpi.config.get("steps_boil_temp", 1) == "99"

    @unittest_run_loop
    async def test_set_get(self):
        value = 35

        await self.cbpi.config.set("steps_cooldown_temp", value)
        assert self.cbpi.config.get("steps_cooldown_temp", 1) == value

    @unittest_run_loop
    async def test_http_set(self):
        value = "Some New Brewery Name"
        key = "BREWERY_NAME"

        resp = await self.client.request("PUT", "/config/%s/" % key, json={'value': value})
        assert resp.status == 204

        assert self.cbpi.config.get(key, -1) == value

    @unittest_run_loop
    async def test_http_get(self):
        resp = await self.client.request("GET", "/config/")
        assert resp.status == 200

    @unittest_run_loop
    async def test_get_default(self):
        value = self.cbpi.config.get("HELLO_WORLD", "DefaultValue")
        assert value == "DefaultValue"