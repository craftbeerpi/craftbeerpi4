from functools import wraps
from aiohttp import web
from .auth import get_auth


def auth_required(func):
    """Utility decorator that checks if a user has been authenticated for this
    request.

    Allows views to be decorated like:

        @auth_required
        def view_func(request):
            pass

    providing a simple means to ensure that whoever is calling the function has
    the correct authentication details.

    Args:
        func: Function object being decorated and raises HTTPForbidden if not

    Returns:
        A function object that will raise web.HTTPForbidden() if the passed
        request does not have the correct permissions to access the view.
    """
    @wraps(func)
    async def wrapper(*args):
        if (await get_auth(args[-1])) is None:
            raise web.HTTPForbidden()

        return await func(*args)

    return wrapper

