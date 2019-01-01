import logging
import os
from os import urandom

from aiohttp import web
from aiohttp_auth import auth
from aiohttp_session import session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_swagger import setup_swagger

from controller.job_controller import JobController
from core.cbpiwebsocket import CBPiWebSocket
from core.controller.actor_controller import ActorController
from core.controller.config_controller import ConfigController
from core.controller.kettle_controller import KettleController
from core.controller.notification_controller import NotificationController
from core.controller.plugin_controller import PluginController
from core.controller.sensor_controller import SensorController
from core.controller.step_controller import StepController
from core.controller.system_controller import SystemController
from core.database.model import DBModel
from core.eventbus import CBPiEventBus
from core.http_endpoints.http_login import Login
from core.utils import *

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class CraftBeerPi():


    def __init__(self):
        self.static_config = load_config(os.path.join(os.path.dirname(__file__), '../config/config.yaml'))

        logger.info("Init CraftBeerPI")

        policy = auth.SessionTktAuthentication(urandom(32), 60, include_ip=True)
        middlewares = [web.normalize_path_middleware(), session_middleware(EncryptedCookieStorage(urandom(32))), auth.auth_middleware(policy)]
        self.app = web.Application(middlewares=middlewares)


        self._setup_shutdownhook()
        self.initializer = []
        self.bus = CBPiEventBus(self.app.loop, self)
        self.ws = CBPiWebSocket(self)
        self.job = JobController(self)
        self.actor = ActorController(self)
        self.sensor = SensorController(self)
        self.plugin = PluginController(self)
        self.system = SystemController(self)
        self.config = ConfigController(self)
        self.kettle = KettleController(self)
        self.step = StepController(self)
        self.notification = NotificationController(self)
        self.login = Login(self)

    def _setup_shutdownhook(self):
        self.shutdown = False
        async def on_cleanup(app):
            self.shutdown = True

        self.app.on_cleanup.append(on_cleanup)


    def register_on_startup(self, obj):

        for method in [getattr(obj, f) for f in dir(obj) if callable(getattr(obj, f)) and hasattr(getattr(obj, f), "on_startup")]:
            name = method.__getattribute__("name")
            order = method.__getattribute__("order")
            self.initializer.append(dict(name=name, method=method, order=order))

    def register(self, obj, url_prefix=None, static=None):

        '''
        This method parses the provided object
        
        :param obj: the object wich will be parsed for registration 
        :param url_prefix: that prefix for HTTP Endpoints
        :return: None
        '''
        self.register_http_endpoints(obj, url_prefix, static)
        self.bus.register_object(obj)
        self.ws.register_object(obj)
        self.job.register_background_task(obj)
        self.register_on_startup(obj)

    def register_http_endpoints(self, obj, url_prefix=None, static=None):
        
        routes = []
        for method in [getattr(obj, f) for f in dir(obj) if callable(getattr(obj, f)) and hasattr(getattr(obj, f), "route")]:
            http_method = method.__getattribute__("method")
            path = method.__getattribute__("path")
            class_name = method.__self__.__class__.__name__
            logger.info("Register Endpoint : %s.%s %s %s%s " % (class_name, method.__name__, http_method, url_prefix, path))

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

        if url_prefix is not None:
            logger.debug("URL Prefix: %s "  % (url_prefix,))
            sub = web.Application()
            sub.add_routes(routes)
            if static is not None:
                sub.add_routes([web.static('/static', static, show_index=False)])
            self.app.add_subapp(url_prefix, sub)
        else:
            self.app.add_routes(routes)

    def _swagger_setup(self):
        '''
        Internatl method to expose REST API documentation by swagger
        
        :return: 
        '''
        long_description = """
        This is the api for CraftBeerPi
        """

        setup_swagger(self.app,
                      description=long_description,
                      title=self.static_config.get("name", "CraftBeerPi"),
                      api_version=self.static_config.get("version", ""),
                      contact="info@craftbeerpi.com")

    def notify(self, key, message, type="info"):
        '''
        This is a convinience method to send notification to the client
        
        :param key: notification key
        :param message: notification message
        :param type: notification type (info,warning,danger,successs)
        :return: 
        '''
        self.bus.sync_fire(topic="notification/%s" % key, key=key, message=message, type=type)

    async def call_initializer(self, app):
        self.initializer = sorted(self.initializer, key=lambda k: k['order'])
        for i in self.initializer:
            logger.info("CALL INITIALIZER %s - %s " % (i["name"], i["method"].__name__))
            await i["method"]()

    def _print_logo(self):
        from pyfiglet import Figlet
        f = Figlet(font='big')
        logger.info("\n%s" % f.renderText("%s %s" % (self.static_config.get("name"), self.static_config.get("version"))))

    async def init_serivces(self):

        self._print_logo()

        await self.job.init()
        await DBModel.setup()
        await self.config.init()
        self.plugin.load_plugins()
        self.plugin.load_plugins_from_evn()
        await self.sensor.init()
        await self.step.init()
        await self.actor.init()
        await self.kettle.init()
        await self.call_initializer(self.app)
        self._swagger_setup()

        return self.app


    def start(self):
        web.run_app(self.init_serivces(), port=self.static_config.get("port", 8080))
