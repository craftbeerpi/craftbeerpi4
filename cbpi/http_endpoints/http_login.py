from aiohttp import web
from aiohttp_auth import auth

from cbpi.api import *


class Login:
    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.cbpi.register(self, url_prefix="/")
        self.db = {
            cbpi.static_config.get("username", "cbpi"): cbpi.static_config.get(
                "password", "cbpi"
            )
        }

    @request_mapping(path="/logout", name="Logout", method="GET", auth_required=True)
    async def logout_view(self, request):
        await auth.forget(request)
        return web.Response(body="OK".encode("utf-8"))

    @request_mapping(path="/login", name="Login", method="POST", auth_required=False)
    async def login_view(self, request):

        params = await request.post()

        user = params.get("username", None)

        if user in self.db and params.get("password", None) == str(self.db[user]):
            # User is in our database, remember their login details
            await auth.remember(request, user)
            return web.Response(body="OK".encode("utf-8"))

        raise web.HTTPForbidden()
