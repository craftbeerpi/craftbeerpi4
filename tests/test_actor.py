from unittest import mock

from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from cbpi.craftbeerpi import CraftBeerPi


class ActorTestCase(AioHTTPTestCase):

    async def get_application(self):
        self.cbpi = CraftBeerPi()
        await self.cbpi.init_serivces()
        return self.cbpi.app

    @unittest_run_loop
    async def test_actor_mock(self):
        with mock.patch.object(self.cbpi.bus, 'fire', wraps=self.cbpi.bus.fire) as mock_obj:
            # Send HTTP POST
            resp = await self.client.request("POST", "/actor/1/on")
            # Check Result
            assert resp.status == 204
            # Check if Event are fired
            assert mock_obj.call_count == 2


    @unittest_run_loop
    async def test_actor_switch(self):

        resp = await self.client.post(path="/login", data={"username": "cbpi", "password": "123"})
        assert resp.status == 200

        resp = await self.client.request("POST", "/actor/1/on")
        assert resp.status == 204
        i = await self.cbpi.actor.get_one(1)
        print(i)
        assert i.instance.state is True

        resp = await self.client.request("POST", "/actor/1/off")
        assert resp.status == 204
        i = await self.cbpi.actor.get_one(1)
        assert i.instance.state is False

        resp = await self.client.request("POST", "/actor/1/toggle")

        assert resp.status == 204
        i = await self.cbpi.actor.get_one(1)
        assert i.instance.state is True

        resp = await self.client.request("POST", "/actor/1/toggle")
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

    @unittest_run_loop
    async def test_crud_negative(self):
        data = {
            "name": "CustomActor",
            "type": "CustomActor",
            "config": {
                "interval": 5
            }
        }

        # Get actor which not exists
        resp = await self.client.get(path="/actor/%s" % 9999)
        assert resp.status == 500

        # Update not existing actor
        resp = await self.client.put(path="/actor/%s" % 9999, json=data)
        assert resp.status == 500

    @unittest_run_loop
    async def test_actor_action(self):
        resp = await self.client.post(path="/actor/1/action", json=dict(name="myAction", parameter=dict(name="Manuel")))
        assert resp.status == 204
