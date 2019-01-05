import aiohttp
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from cbpi.craftbeerpi import CraftBeerPi


class NotificationTestCase(AioHTTPTestCase):

    async def get_application(self):
        self.cbpi = CraftBeerPi()
        await self.cbpi.init_serivces()
        return self.cbpi.app


    @unittest_run_loop
    async def test_actor_switch(self):
        self.cbpi.notify("test", "test")