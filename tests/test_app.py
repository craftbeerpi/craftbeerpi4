from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from core.craftbeerpi import CraftBeerPi


class MyAppTestCase(AioHTTPTestCase):




    async def get_application(self):
        self.cbpi = CraftBeerPi()
        return self.cbpi.app


    @unittest_run_loop
    async def test_example(self):

        #resp = await self.client.request("GET", "/actor/1/on")
        #print(resp.status)
        #assert resp.status == 204
        for i in range(1000):
            resp = await self.client.request("GET", "/actor/hallo")

            assert resp.status == 200

        #text = await resp.json()
        #pprint(text)
        '''
        resp = await self.client.request("GET", "/actor/2")
        print(resp.status)
        assert resp.status == 200
        text = await resp.json()
        pprint(text)
        '''
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

