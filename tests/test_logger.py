import asyncio
import glob

from aiohttp.test_utils import unittest_run_loop
from tests.cbpi_config_fixture import CraftBeerPiTestCase
import os

class LoggerTestCase(CraftBeerPiTestCase):

    @unittest_run_loop
    async def test_log_data(self):

        os.makedirs("./logs", exist_ok=True)
        log_name = "test"
        #clear all logs
        self.cbpi.log.clear_log(log_name)
        assert len(glob.glob('./logs/sensor_%s.log*' % log_name)) == 0

        # write log entries
        for i in range(5):
            print(log_name)
            self.cbpi.log.log_data(log_name, 222)
            await asyncio.sleep(1)

        # read log data
        data = await self.cbpi.log.get_data(log_name, sample_rate='1s')
        assert len(data["time"]) == 5

        assert self.cbpi.log.zip_log_data(log_name) is not None

        self.cbpi.log.clear_zip(log_name)

        self.cbpi.log.clear_log(log_name)



