from functools import wraps

from voluptuous import Schema

__all__ = ["request_mapping", "on_startup", "on_event", "action", "background_task"]

from aiohttp_auth import auth

def composed(*decs):
    def deco(f):
        for dec in reversed(decs):
            f = dec(f)
        return f
    return deco

def request_mapping(path, name=None, method="GET", auth_required=True, json_schema=None):

    def on_http_request(path, name=None):
        def real_decorator(func):
            func.route = True
            func.path = path
            func.name = name
            func.method = method
            return func

        return real_decorator

    def validate_json_body(func):


        @wraps(func)
        async def wrapper(*args):

            if json_schema is not None:
                data = await args[-1].json()
                schema = Schema(json_schema)
                schema(data)

            return await func(*args)

        return wrapper



    if auth_required is True:
        return composed(
            on_http_request(path, name),
            auth.auth_required,
            validate_json_body

        )
    else:
        return composed(
            on_http_request(path, name),
            validate_json_body
        )

def on_event(topic):
    def real_decorator(func):
        func.eventbus = True
        func.topic = topic
        func.c = None
        return func

    return real_decorator

def action(key, parameters):
    def real_decorator(func):
        func.action = True
        func.key = key
        func.parameters = parameters
        return func

    return real_decorator

def background_task(name, interval):
    def real_decorator(func):
        func.background_task = True
        func.name = name
        func.interval = interval
        return func
    return real_decorator


def on_startup(name, order=0):
    def real_decorator(func):
        func.on_startup = True
        func.name = name
        func.order = order
        return func
    return real_decorator


def entry_exit(f):
    def new_f():

        f()

    return new_f