import asyncio
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from core.craftbeerpi import CraftBeerPi


class KettleTestCase(AioHTTPTestCase):


    async def get_application(self):
        self.cbpi = CraftBeerPi()
        await self.cbpi.init_serivces()
        return self.cbpi.app

    @unittest_run_loop
    async def test_get(self):

        resp = await self.client.request("GET", "/kettle")
        assert resp.status == 200
        print(await resp.json())

    @unittest_run_loop
    async def test_add(self):
        data = {
            "name": "Test",
            "sensor": None,
            "heater": "1",
            "automatic": None,
            "logic": "CustomKettleLogic",
            "config": {
                "test": "WOOHO"
            },
            "agitator": None,
            "target_temp": None
        }

        resp = await self.client.post(path="/kettle/", json=data)
        assert resp.status == 200

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