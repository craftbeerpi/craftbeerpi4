import logging
import unittest

from cli import add, remove, list_plugins

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')


class CLITest(unittest.TestCase):

    def test_install(self):
        assert add("cbpi4-ui-plugin") == True
        assert add("cbpi4-ui-plugin") == False
        assert remove("cbpi4-ui-plugin") == True

    def test_list(self):
        list_plugins()

if __name__ == '__main__':
    unittest.main()