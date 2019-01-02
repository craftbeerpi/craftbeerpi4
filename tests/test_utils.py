from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from core.craftbeerpi import CraftBeerPi, load_config


class UtilsTestCase(AioHTTPTestCase):

    async def get_application(self):
        self.cbpi = CraftBeerPi()
        await self.cbpi.init_serivces()
        return self.cbpi.app

    @unittest_run_loop
    async def test_load_file(self):
        assert load_config("") is None