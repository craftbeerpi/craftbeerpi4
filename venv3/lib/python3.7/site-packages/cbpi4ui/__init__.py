import os

from aiohttp import web
from cbpi.api import *

class CBPiUi(CBPiExtension):

    @request_mapping(path="/", auth_required=False)
    async def hello_world(self, request):
        return web.Response(text="Hello, world")

    def __init__(self, cbpi):
        self.cbpi = cbpi
        path = os.path.dirname(__file__)
        self.cbpi.register(self, "/cbpi_ui", static=os.path.join(path, "build"))

def setup(cbpi):

    cbpi.plugin.register("UI", CBPiUi)
