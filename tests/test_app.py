import aiohttp
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from core.craftbeerpi import CraftBeerPi


class MyAppTestCase(AioHTTPTestCase):




    async def get_application(self):
        self.cbpi = CraftBeerPi()
        self.cbpi.setup()

        await self.cbpi.init_serivces()
        return self.cbpi.app


    @unittest_run_loop
    async def test_example(self):

        resp = await self.client.post(path="/login", data={"username": "cbpi", "password": "123"})
        print("resp.status",resp.status)
        assert resp.status == 200

        resp = await self.client.request("GET", "/actor/1/on")
        print("resp.status", resp.status)
        assert resp.status == 204
        i = await self.cbpi.actor.get_one(1)
        assert i.instance.state is True

        resp = await self.client.request("GET", "/actor/1/off")
        assert resp.status == 204
        i = await self.cbpi.actor.get_one(1)
        assert i.instance.state is False

        resp = await self.client.request("GET", "/actor/1/toggle")

        assert resp.status == 204
        i = await self.cbpi.actor.get_one(1)
        assert i.instance.state is True

        resp = await self.client.request("GET", "/actor/1/toggle")
        assert resp.status == 204
        i = await self.cbpi.actor.get_one(1)
        assert i.instance.state is False

        i = await self.cbpi.actor.get_all()
        assert len(i) == 2
        #ws =  await self.client.ws_connect("/ws");
        #await ws.send_str(json.dumps({"key": "test"}))


'''
    @unittest_run_loop
    async def test_example2(self):
        print("TEST2222")

        print("CLIENT ###### ", self.client)




        ws = await self.client.ws_connect("/ws");
        await ws.send_str(json.dumps({"topic": "test"}))



        #resp = await ws.receive()

        #print("##### REPSONE", resp)
        assert "Manuel" in await self.cbpi.actor.get_name(), "OH NOW"

        await self.client.close()

'''

