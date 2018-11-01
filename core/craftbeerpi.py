import asyncio
import importlib
import logging
from os import urandom

import yaml
from aiohttp import web
from aiohttp_auth import auth
from aiohttp_session import session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_swagger import setup_swagger
from aiojobs.aiohttp import setup, get_scheduler_from_app

from core.controller.actor_controller import ActorController
from core.controller.sensor_controller import SensorController
from core.controller.system_controller import SystemController
from core.database.model import DBModel
from core.eventbus import EventBus
from core.http_endpoints.http_login import Login
from core.websocket import WebSocket

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


class CraftBeerPi():
    def __init__(self):

        logger.info("Init CraftBeerPI")
        policy = auth.SessionTktAuthentication(urandom(32), 60, include_ip=True)
        middlewares = [session_middleware(EncryptedCookieStorage(urandom(32))), auth.auth_middleware(policy)]
        self.app = web.Application(middlewares=middlewares)

        setup(self.app)
        self.bus = EventBus()
        self.ws = WebSocket(self)
        self.actor = ActorController(self)
        self.sensor = SensorController(self)
        self.system = SystemController(self)
        self.login = Login(self)

    def register_events(self, obj):

        for method in [getattr(obj, f) for f in dir(obj) if callable(getattr(obj, f)) and hasattr(getattr(obj, f), "eventbus")]:
            print(method.__getattribute__("topic"), method)

            doc = None
            if method.__doc__ is not None:
                doc = yaml.load(method.__doc__)
                doc["topic"] = method.__getattribute__("topic")
            self.bus.register(method.__getattribute__("topic"), method, doc)

    def register_background_task(self, obj):
        for method in [getattr(obj, f) for f in dir(obj) if callable(getattr(obj, f)) and hasattr(getattr(obj, f), "background_task")]:
            name = method.__getattribute__("name")
            interval = method.__getattribute__("interval")

            async def job_loop(app, name, interval, method):
                logger.info("Start Background Task %s Interval %s Method %s" % (name, interval, method))
                while True:
                    logger.info("Execute Task %s - interval(%s second(s)" % (name, interval))
                    await asyncio.sleep(interval)
                    await method()

            async def spawn_job(app):
                scheduler = get_scheduler_from_app(self.app)
                await scheduler.spawn(job_loop(self.app, name, interval, method))

            self.app.on_startup.append(spawn_job)

    def register_ws(self, obj):
        if self.ws is None:
            return

        for method in [getattr(obj, f) for f in dir(obj) if callable(getattr(obj, f)) and hasattr(getattr(obj, f), "ws")]:
            self.ws.add_callback(method, method.__getattribute__("key"))

    def register(self, obj, subapp=None):
        self.register_http_endpoints(obj, subapp)
        self.register_events(obj)
        self.register_ws(obj)
        self.register_background_task(obj)

    def register_http_endpoints(self, obj, subapp=None):
        routes = []
        for method in [getattr(obj, f) for f in dir(obj) if callable(getattr(obj, f)) and hasattr(getattr(obj, f), "route")]:
            http_method = method.__getattribute__("method")
            path = method.__getattribute__("path")
            class_name = method.__self__.__class__.__name__
            logger.info("Register Endpoint : %s.%s %s %s%s " % (class_name, method.__name__, http_method, subapp, path))

            def add_post():
                routes.append(web.post(method.__getattribute__("path"), method))

            def add_get():
                routes.append(web.get(method.__getattribute__("path"), method))

            def add_delete():
                routes.append(web.delete(path, method))

            def add_put():
                routes.append(web.put(path, method))

            switcher = {
                "POST": add_post,
                "GET": add_get,
                "DELETE": add_delete,
                "PUT": add_put
            }

            switcher[http_method]()

        if subapp is not None:
            sub = web.Application()
            sub.add_routes(routes)
            self.app.add_subapp(subapp, sub)
        else:
            self.app.add_routes(routes)

    async def _load_extensions(self, app):
        extension_list = ["core.extension.dummy"]

        for extension in extension_list:
            logger.info("LOADING PUGIN %s" % extension)
            my_module = importlib.import_module(extension)
            my_module.setup(self)

    def start(self):

        async def init_database(app):
            await DBModel.test_connection()

        async def init_controller(app):
            await self.actor.init()

        self.app.on_startup.append(init_database)
        self.app.on_startup.append(self._load_extensions)
        self.app.on_startup.append(init_controller)
        setup_swagger(self.app)
        web.run_app(self.app)
