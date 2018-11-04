import asyncio
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
from core.controller.plugin_controller import PluginController
from core.controller.sensor_controller import SensorController
from core.controller.system_controller import SystemController
from core.database.model import DBModel
from core.eventbus import EventBus
from core.http_endpoints.http_login import Login
from core.utils import *
from core.websocket import WebSocket

logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)


class CraftBeerPi():

    def __init__(self):
        self.config = load_config("./config/config.yaml")

        logger.info("Init CraftBeerPI")
        policy = auth.SessionTktAuthentication(urandom(32), 60, include_ip=True)
        middlewares = [session_middleware(EncryptedCookieStorage(urandom(32))), auth.auth_middleware(policy)]
        self.app = web.Application(middlewares=middlewares)
        self.initializer = []

        setup(self.app)
        self.bus = EventBus()
        self.ws = WebSocket(self)
        self.actor = ActorController(self)
        self.sensor = SensorController(self)
        self.plugin = PluginController(self)
        self.system = SystemController(self)

        self.login = Login(self)

    def register_events(self, obj):

        for method in [getattr(obj, f) for f in dir(obj) if callable(getattr(obj, f)) and hasattr(getattr(obj, f), "eventbus")]:

            doc = None
            if method.__doc__ is not None:
                doc = yaml.load(method.__doc__)
                doc["topic"] = method.__getattribute__("topic")
            self.bus.register(method.__getattribute__("topic"), method, doc)

    def register_background_task(self, obj):


        async def job_loop(app, name, interval, method):
            logger.info("Start Background Task %s Interval %s Method %s" % (name, interval, method))
            while True:
                logger.info("Execute Task %s - interval(%s second(s)" % (name, interval))
                await asyncio.sleep(interval)
                await method()

        async def spawn_job(app):
            scheduler = get_scheduler_from_app(self.app)
            for method in [getattr(obj, f) for f in dir(obj) if callable(getattr(obj, f)) and hasattr(getattr(obj, f), "background_task")]:
                name = method.__getattribute__("name")
                interval = method.__getattribute__("interval")

                await scheduler.spawn(job_loop(self.app, name, interval, method))

        self.app.on_startup.append(spawn_job)


    def register_on_startup(self, obj):

        for method in [getattr(obj, f) for f in dir(obj) if callable(getattr(obj, f)) and hasattr(getattr(obj, f), "on_startup")]:

            name = method.__getattribute__("name")
            order = method.__getattribute__("order")

            self.initializer.append(dict(name=name, method=method, order=order))



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
        self.register_on_startup(obj)

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

    def _swagger_setup(self):

        long_description = """
        Lorem ipsum dolor sit amet, consectetur adipiscing elit. Phasellus vehicula, metus et sodales fringilla, purus leo aliquet odio, non tempor ante urna aliquet nibh. Integer accumsan laoreet tincidunt. Vestibulum semper vehicula sollicitudin. Suspendisse dapibus neque vitae mattis bibendum. Morbi eu pulvinar turpis, quis malesuada ex. Vestibulum sed maximus diam. Proin semper fermentum suscipit. Duis at suscipit diam. Integer in augue elementum, auctor orci ac, elementum est. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Maecenas condimentum id arcu quis volutpat. Vestibulum sit amet nibh sodales, iaculis nibh eget, scelerisque justo.

        Nunc eget mauris lectus. Proin sit amet volutpat risus. Aliquam auctor nunc sit amet feugiat tempus. Maecenas nec ex dolor. Nam fermentum, mauris ut suscipit varius, odio purus luctus mauris, pretium interdum felis sem vel est. Proin a turpis vitae nunc volutpat tristique ac in erat. Pellentesque consequat rhoncus libero, ac sollicitudin odio tempus a. Sed vestibulum leo erat, ut auctor turpis mollis id. Ut nec nunc ex. Maecenas eu turpis in nibh placerat ullamcorper ac nec dui. Integer ac lacus neque. Donec dictum tellus lacus, a vulputate justo venenatis at. Morbi malesuada tellus quis orci aliquet, at vulputate lacus imperdiet. Nulla eu diam quis orci aliquam vulputate ac imperdiet elit. Quisque varius mollis dolor in interdum.
        """

        setup_swagger(self.app,
                      description=long_description,
                      title=self.config.get("name", "CraftBeerPi"),
                      api_version=self.config.get("version", ""),
                      contact="info@craftbeerpi.com")



    def start(self):

        from pyfiglet import Figlet
        f = Figlet(font='big')
        print(f.renderText("%s %s" % (self.config.get("name"), self.config.get("version"))))

        async def init_database(app):
            await DBModel.test_connection()

        async def init_controller(app):
            await self.actor.init()

        async def load_plugins(app):
            await PluginController.load_plugin_list()
            await PluginController.load_plugins()

        async def call_initializer(app):

            self.initializer = sorted(self.initializer, key=lambda k: k['order'])
            for i in self.initializer:
                logger.info("CALL INITIALIZER %s - %s " % (i["name"], i["method"].__name__))

                await i["method"]()


        self.app.on_startup.append(init_database)
        self.app.on_startup.append(call_initializer)
        self.app.on_startup.append(init_controller)
        self.app.on_startup.append(load_plugins)
        self._swagger_setup()
        web.run_app(self.app, port=self.config.get("port", 8080))
