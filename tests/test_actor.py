import aiohttp
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from core.craftbeerpi import CraftBeerPi


class ActorTestCase(AioHTTPTestCase):




    async def get_application(self):
        self.cbpi = CraftBeerPi()
        await self.cbpi.init_serivces()
        return self.cbpi.app


    @unittest_run_loop
    async def test_actor_switch(self):

        resp = await self.client.post(path="/login", data={"username": "cbpi", "password": "123"})
        assert resp.status == 200

        resp = await self.client.request("GET", "/actor/1/on")
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

    @unittest_run_loop
    async def test_crud(self):
        data = {
            "name": "CustomActor",
            "type": "CustomActor",
            "config": {
                "interval": 5
            }
        }

        # Add new sensor
        resp = await self.client.post(path="/actor/", json=data)
        assert resp.status == 200

        m = await resp.json()
        sensor_id = m["id"]

        # Get sensor
        resp = await self.client.get(path="/actor/%s" % sensor_id)
        assert resp.status == 200

        m2 = await resp.json()
        sensor_id = m2["id"]

        # Update Sensor
        resp = await self.client.put(path="/actor/%s" % sensor_id, json=m)
        assert resp.status == 200

        # # Delete Sensor
        resp = await self.client.delete(path="/actor/%s" % sensor_id)
        assert resp.status == 204
