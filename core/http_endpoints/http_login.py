from aiohttp import web
from aiohttp_auth import auth

class Login():

    def __init__(self, core):
        core.app.router.add_route('POST', '/login', self.login_view)
        core.app.router.add_route('GET', '/logout', self.logout_view)
        self.db = {'user': 'password', 'super_user': 'super_password'}

    @auth.auth_required
    async def logout_view(self, request):
        await auth.forget(request)
        return web.Response(body='OK'.encode('utf-8'))

    async def login_view(self, request):
        params = await request.post()
        print("HALLO LOGIN")
        print(params.get('username', None), params.get('password', None))
        user = params.get('username', None)
        if (user in self.db and
            params.get('password', None) == self.db[user]):

            # User is in our database, remember their login details
            await auth.remember(request, user)
            return web.Response(body='OK'.encode('utf-8'))

        raise web.HTTPForbidden()

