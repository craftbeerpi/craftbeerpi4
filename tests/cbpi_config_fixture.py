# content of conftest.py
from codecs import ignore_errors
from distutils.command.config import config
import os
from cbpi.configFolder import ConfigFolder
from cbpi.craftbeerpi import CraftBeerPi
from aiohttp.test_utils import AioHTTPTestCase
from distutils.dir_util import copy_tree


class CraftBeerPiTestCase(AioHTTPTestCase):

    async def get_application(self):
        self.config_folder = self.configuration()
        self.cbpi = CraftBeerPi(self.config_folder)
        await self.cbpi.init_serivces()
        return self.cbpi.app

    def configuration(self):
        test_directory = os.path.dirname(__file__)
        test_config_directory = os.path.join(test_directory, 'cbpi-test-config')
        configFolder = ConfigFolder(test_config_directory)
        return configFolder
