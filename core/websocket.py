import logging
import weakref
from collections import defaultdict

import aiohttp
from aiohttp import web
from typing import Iterable, Callable


class WebSocket:
    def __init__(self, cbpi) -> None:
        self.cbpi = cbpi
        self._callbacks = defaultdict(set)
        self._clients = weakref.WeakSet()
        self.logger = logging.getLogger(__name__)
        self.cbpi.app.add_routes([web.get('/ws', self.websocket_handler)])

    def add_callback(self, func: Callable, event: str) -> None:
        self._callbacks[event].add(func)

    async def emit(self, event: str, *args, **kwargs) -> None:
        for func in self._event_funcs(event):
            await func(*args, **kwargs)

    def _event_funcs(self, event: str) -> Iterable[Callable]:
        for func in self._callbacks[event]:
            yield func

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self._clients.add(ws)

        c = len(self._clients) - 1

        self.logger.info(ws)
        self.logger.info(c)
        try:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == 'close':

                        await ws.close()
                        self.logger.info("WS Close")
                    else:
                        msg_obj = msg.json()

                        self.cbpi.bus.fire(msg_obj["topic"], id=1, power=22)
                        # await self.fire(msg_obj["key"], ws, msg)

                        # await ws.send_str(msg.data)
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    self.logger.error('ws connection closed with exception %s' % ws.exception())

        finally:
            self._clients.discard(ws)

        self.logger.info("Web Socket Close")

        return ws


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    _ws.append(ws)

    c = len(_ws) - 1

    async for msg in ws:

        if msg.type == aiohttp.WSMsgType.TEXT:
            if msg.data == 'close':
                await ws.close()
            else:

                await ws.send_str(msg.data)
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())

    del _ws[c]
    print('websocket connection closed')

    return ws
