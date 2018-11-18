import asyncio
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from core.craftbeerpi import CraftBeerPi


class KettleTestCase(AioHTTPTestCase):


    async def get_application(self):
        self.cbpi = CraftBeerPi()
        self.cbpi.setup()
        return self.cbpi.app


    @unittest_run_loop
    async def test_example(self):
        assert await self.cbpi.kettle.toggle_automtic(1) is True
        assert await self.cbpi.kettle.toggle_automtic(1) is True
        assert await self.cbpi.kettle.toggle_automtic(99) is False
