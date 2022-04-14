from aiohttp.test_utils import unittest_run_loop
from tests.cbpi_config_fixture import CraftBeerPiTestCase


class NotificationTestCase(CraftBeerPiTestCase):

    @unittest_run_loop
    async def test_actor_switch(self):
        self.cbpi.notify("test", "test")