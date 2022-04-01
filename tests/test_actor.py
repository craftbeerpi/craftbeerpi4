import logging
from unittest import mock
from aiohttp.test_utils import unittest_run_loop
from tests.cbpi_config_fixture import CraftBeerPiTestCase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')


class ActorTestCase(CraftBeerPiTestCase):

    @unittest_run_loop
    async def test_actor_switch(self):

        resp = await self.client.post(path="/login", data={"username": "cbpi", "password": "123"})
        assert resp.status == 200, "login should be successful"

        resp = await self.client.request("POST", "/actor/3CUJte4bkxDMFCtLX8eqsX/on")
        assert resp.status == 204, "switching actor on should work"
        i = self.cbpi.actor.find_by_id("3CUJte4bkxDMFCtLX8eqsX")

        assert i.instance.state is True

        resp = await self.client.request("POST", "/actor/3CUJte4bkxDMFCtLX8eqsX/off")
        assert resp.status == 204
        i = self.cbpi.actor.find_by_id("3CUJte4bkxDMFCtLX8eqsX")
        assert i.instance.state is False

    @unittest_run_loop
    async def test_crud(self):
        data = {
            "name": "SomeActor",
            "power": 100,
            "props": {
            },
            "state": False,
            "type": "DummyActor"
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

        resp = await self.client.request("POST", "/actor/%s/on" % sensor_id)
        assert resp.status == 204



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
