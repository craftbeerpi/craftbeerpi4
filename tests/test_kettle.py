import asyncio
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from core.craftbeerpi import CraftBeerPi


class MyAppTestCase(AioHTTPTestCase):




    async def get_application(self):
        self.cbpi = CraftBeerPi()
        self.cbpi.setup()
        return self.cbpi.app


    @unittest_run_loop
    async def test_example(self):

        await self.cbpi.kettle.toggle_automtic(1)
