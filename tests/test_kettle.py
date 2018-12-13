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
        await asyncio.sleep(10)
        for i in range(100):
            resp = await self.client.request("GET", "/actor/")
            print(resp)
            resp = await self.client.post(path="/actor/", json={ "name": "Test", "type": "CustomActor", "config": {"gpio": 22 }})
            print(resp)


        '''
        result = await self.cbpi.kettle.toggle_automtic(1)
        print("#### RESULT", result)
        assert result[0] is True
        print("FIRE")


        await asyncio.sleep(1)

        self.cbpi.bus.fire("actor/1/on", id=1)


        await asyncio.sleep(5)
        #assert await self.cbpi.kettle.toggle_automtic(1) is True
        #assert await self.cbpi.kettle.toggle_automtic(99) is False
        '''