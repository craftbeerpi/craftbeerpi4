import aiohttp
from aiohttp.test_utils import unittest_run_loop
from tests.cbpi_config_fixture import CraftBeerPiTestCase

# class WebSocketTestCase(CraftBeerPiTestCase):

#     @unittest_run_loop
#     async def test_brewing_process(self):

#         count_step_done = 0
#         async with self.client.ws_connect('/ws') as ws:
#             await ws.send_json(data=dict(topic="step/stop"))
#             await ws.send_json(data=dict(topic="step/start"))
#             async for msg in ws:
#                 if msg.type == aiohttp.WSMsgType.TEXT:
#                     try:
#                         msg_obj = msg.json()
#                         topic = msg_obj.get("topic")
#                         if topic == "job/step/done":
#                             count_step_done = count_step_done + 1
#                         if topic == "step/brewing/finished":
#                             await ws.send_json(data=dict(topic="close"))
#                     except Exception as e:
#                         print(e)
#                         break
#                 elif msg.type == aiohttp.WSMsgType.ERROR:
#                     break

#         assert count_step_done == 4

#     @unittest_run_loop
#     async def test_wrong_format(self):

#         async with self.client.ws_connect('/ws') as ws:
#             await ws.send_json(data=dict(a="close"))
#             async for msg in ws:
#                 print("MSG TYP", msg.type, msg.data)
#                 if msg.type == aiohttp.WSMsgType.TEXT:
#                     msg_obj = msg.json()
#                     if msg_obj["topic"] != "connection/success":
#                         print(msg.data)
#                         raise Exception()

#                 else:
#                     raise Exception()

