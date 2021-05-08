import aiohttp
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

from cbpi.craftbeerpi import CraftBeerPi


class DashboardTestCase(AioHTTPTestCase):
    async def get_application(self):
        self.cbpi = CraftBeerPi()
        await self.cbpi.init_serivces()
        return self.cbpi.app

    @unittest_run_loop
    async def test_crud(self):
        data = {
            "name": "MyDashboard",
        }

        dashboard_content = {"type": "Test", "x": 0, "y": 0, "config": {}}

        resp = await self.client.get(path="/dashboard")
        assert resp.status == 200

        # Add new dashboard
        resp = await self.client.post(path="/dashboard/", json=data)
        assert resp.status == 200

        m = await resp.json()
        dashboard_id = m["id"]

        # Get dashboard
        resp = await self.client.get(path="/dashboard/%s" % dashboard_id)
        assert resp.status == 200

        m2 = await resp.json()
        dashboard_id = m2["id"]

        # Update dashboard
        resp = await self.client.put(path="/dashboard/%s" % dashboard_id, json=m)
        assert resp.status == 200

        # Add dashboard content
        dashboard_content["dbid"] = dashboard_id
        resp = await self.client.post(
            path="/dashboard/%s/content" % dashboard_id, json=dashboard_content
        )
        assert resp.status == 200
        m_content = await resp.json()
        print("CONTENT", m_content)
        content_id = m_content["id"]
        # Get dashboard
        resp = await self.client.get(path="/dashboard/%s/content" % (dashboard_id))
        assert resp.status == 200

        resp = await self.client.post(
            path="/dashboard/%s/content/%s/move" % (dashboard_id, content_id),
            json=dict(x=1, y=1),
        )
        assert resp.status == 200

        resp = await self.client.delete(
            path="/dashboard/%s/content/%s" % (dashboard_id, content_id)
        )
        assert resp.status == 204

        # Delete dashboard
        resp = await self.client.delete(path="/dashboard/%s" % dashboard_id)
        assert resp.status == 204

    @unittest_run_loop
    async def test_dashboard_controller(self):
        result = await self.cbpi.dashboard.get_all()
        print(result)

        await self.cbpi.dashboard.add(**{"name": "Tewst"})
        print(await self.cbpi.dashboard.get_one(1))

        await self.cbpi.dashboard.add_content(
            dict(dbid=1, element_id=1, type="test", config={"name": "Manue"})
        )
        await self.cbpi.dashboard.move_content(1, 2, 3)
