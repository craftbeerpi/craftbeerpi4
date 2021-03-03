import logging
from unittest import mock
import unittest
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from cbpi.craftbeerpi import CraftBeerPi
import pprint
import asyncio
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
pp = pprint.PrettyPrinter(indent=4)

class ActorTestCase(AioHTTPTestCase):

    async def get_application(self):
        self.cbpi = CraftBeerPi()
        await self.cbpi.init_serivces()
        return self.cbpi.app
    '''
    @unittest_run_loop
    async def test_get_all(self):
        resp = await self.client.get(path="/step2")
        assert resp.status == 200
    
    @unittest_run_loop
    async def test_add_step(self):
        resp = await self.client.post(path="/step2", json=dict(name="Manuel"))
        data = await resp.json()
        assert resp.status == 200
    
    @unittest_run_loop
    async def test_delete(self):
        
        resp = await self.client.post(path="/step2", json=dict(name="Manuel"))
        data = await resp.json()
        assert resp.status == 200
        resp = await self.client.delete(path="/step2/%s" % data["id"])
        assert resp.status == 204
    '''    

    @unittest_run_loop
    async def test_move(self):
        await self.cbpi.step2.resume()
    

        
if __name__ == '__main__':
    unittest.main()