import logging
from os import urandom

from aiohttp import web
from aiohttp_auth import auth
from aiohttp_session import session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_swagger import setup_swagger
from cbpi.api.exceptions import CBPiException
from voluptuous import MultipleInvalid

from cbpi.controller.dashboard_controller import DashboardController
from cbpi.controller.job_controller import JobController
from cbpi.controller.actor_controller import ActorController
from cbpi.controller.config_controller import ConfigController
from cbpi.controller.kettle_controller import KettleController
from cbpi.controller.notification_controller import NotificationController
from cbpi.controller.plugin_controller import PluginController
from cbpi.controller.sensor_controller import SensorController
from cbpi.controller.step_controller import StepController
from cbpi.controller.system_controller import SystemController
from cbpi.database.model import DBModel
from cbpi.eventbus import CBPiEventBus
from cbpi.http_endpoints.http_login import Login
from cbpi.utils import *
from cbpi.websocket import CBPiWebSocket
from cbpi.http_endpoints.http_actor import ActorHttpEndpoints
from cbpi.http_endpoints.http_config import ConfigHttpEndpoints
from cbpi.http_endpoints.http_dashboard import DashBoardHttpEndpoints
from cbpi.http_endpoints.http_kettle import KettleHttpEndpoints
from cbpi.http_endpoints.http_sensor import SensorHttpEndpoints
from cbpi.http_endpoints.http_step import StepHttpEndpoints


logger = logging.getLogger(__name__)




@web.middleware
async def error_middleware(request, handler):
    try:
        response = await handler(request)
        if response.status != 404:
            return response
        message = response.message
    except web.HTTPException as ex:
        if ex.status != 404:
            raise
        message = ex.reason
    except CBPiException as ex:
        message = str(ex)
        return web.json_response(status=500, data={'error': message})
    except MultipleInvalid as ex:
        return web.json_response(status=500, data={'error': str(ex)})
    return web.json_response({'error': message})

class CraftBeerPi():

    def __init__(self):


        self.static_config = load_config("./config/config.yaml")
        self.database_file = "./craftbeerpi.db"
        logger.info("Init CraftBeerPI")

        policy = auth.SessionTktAuthentication(urandom(32), 60, include_ip=True)
        middlewares = [web.normalize_path_middleware(), session_middleware(EncryptedCookieStorage(urandom(32))), auth.auth_middleware(policy), error_middleware]
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
        self.dashboard = DashboardController(self)

        self.http_step = StepHttpEndpoints(self)
        self.http_sensor = SensorHttpEndpoints(self)
        self.http_config = ConfigHttpEndpoints(self)
        self.http_actor = ActorHttpEndpoints(self)
        self.http_kettle = KettleHttpEndpoints(self)
        self.http_dashboard = DashBoardHttpEndpoints(self)

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
        #self.ws.register_object(obj)
        self.job.register_background_task(obj)
        self.register_on_startup(obj)

    def register_http_endpoints(self, obj, url_prefix=None, static=None):

        if url_prefix is None:
            logger.debug("URL Prefix is None for %s. No endpoints will be registered. Please set / explicit if you want to add it to the root path" % obj)
            return

        routes = []
        for method in [getattr(obj, f) for f in dir(obj) if callable(getattr(obj, f)) and hasattr(getattr(obj, f), "route")]:
            http_method = method.__getattribute__("method")
            path = method.__getattribute__("path")
            class_name = method.__self__.__class__.__name__
            logger.info("Register Endpoint : %s.%s %s %s%s " % (class_name, method.__name__, http_method, url_prefix, path))

            def add_post():
                routes.append(web.post(method.__getattribute__("path"), method))

            def add_get():
                routes.append(web.get(method.__getattribute__("path"), method, allow_head=False))

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

        if url_prefix != "/":
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


    def _setup_http_index(self):
        async def http_index(request):
            url = self.config.static.get("index_url")
            if url is not None:
                raise web.HTTPFound(url)
            else:
                return web.Response(text="Hello, world")

        self.app.add_routes([web.get('/', http_index)])

    async def init_serivces(self):

        self._print_logo()

        await self.job.init()
        await DBModel.setup()
        await self.config.init()

        self._setup_http_index()
        self.plugin.load_plugins()
        self.plugin.load_plugins_from_evn()
        await self.sensor.init()
        await self.step.init()
        await self.actor.init()
        await self.kettle.init()
        await self.call_initializer(self.app)
        await self.dashboard.init()
        self._swagger_setup()

        return self.app


    def start(self):
        web.run_app(self.init_serivces(), port=self.static_config.get("port", 8080))
