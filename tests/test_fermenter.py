import asyncio
from cbpi.api.dataclasses import Fermenter, FermenterStep, Props, Step
import logging
from unittest import mock
from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop
from cbpi.craftbeerpi import CraftBeerPi
from cbpi.controller.fermentation_controller import FermenationController
import unittest
import json
from aiohttp import web
from unittest.mock import MagicMock, Mock
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')


class FermenterTest(AioHTTPTestCase):

    async def get_application(self):
        app = web.Application()
        return app

    def create_file(self):

        data = [
            {
                "id": "f1",
                "name": "Fermenter1",
                "props": {},
                "steps": [
                    {
                        "id": "f1s1",
                        "name": "Step1",
                        "props": {},
                        "state_text": "",
                        "status": "I",
                        "type": "T2"
                    },
                    {
                        "id": "f1s2",
                        "name": "Step2",
                        "props": {},
                        "state_text": "",
                        "status": "I",
                        "type": "T1"
                    },
                ],
                "target_temp": 0
            },
            {
                "id": "f2",
                "name": "Fermenter2",
                "props": {},
                "steps": [
                    {
                        "id": "f2s1",
                        "name": "Step1",
                        "props": {},
                        "state_text": "",
                        "status": "I",
                        "type": "T1"
                    },
                    {
                        "id": "f2s2",
                        "name": "Step2",
                        "props": {},
                        "state_text": "",
                        "status": "I",
                        "type": "T2"
                    },
                ],
                "target_temp": 0
            }
        ]

        with open("./config/fermenter_data.json", "w") as file:
            json.dump(data, file, indent=4, sort_keys=True)


    @unittest_run_loop
    async def test_actor_mock(self):
        self.create_file()
        mock = Mock()
        f = FermenationController(mock)

        f.types = {
            "T1": {"name": "T2", "class": FermenterStep, "properties": [], "actions": []},
            "T2": {"name": "T2", "class": FermenterStep, "properties": [], "actions": []}
        }
        await f.load()
        #ferm = Fermenter(name="Maneul")
        # item = await f.create(ferm)
        # await f.create_step(item.id, Step(name="Manuel"))
        # await f.delete(item.id)

        item = await f.get("f1")

        await f.start("f1")
        await f.start("f2")
        await asyncio.sleep(3)
        # await f.create_step(item.id, Step(name="MANUEL", props=Props()))

        #await f.start(item.id)
        #await asyncio.sleep(1)
        #await f.next(item.id)
        #await asyncio.sleep(1)
        #await f.next(item.id)
        #await asyncio.sleep(1)
        #await f.next(item.id)
        #await asyncio.sleep(1)
        #await f.move_step("f1", "f1s1", 1)
        # await f.reset(item.id)
        await f.shutdown()


if __name__ == '__main__':
    unittest.main()
