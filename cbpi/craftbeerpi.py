
import asyncio
import sys
try:
    from asyncio import set_event_loop_policy, WindowsSelectorEventLoopPolicy
except ImportError:
    pass
import json
from voluptuous.schema_builder import message
from cbpi.api.dataclasses import NotificationType
from cbpi.controller.notification_controller import NotificationController
import logging
from os import urandom
import os
from cbpi import __version__, __codename__
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
from cbpi.controller.plugin_controller import PluginController
from cbpi.controller.sensor_controller import SensorController
from cbpi.controller.step_controller import StepController
from cbpi.controller.recipe_controller import RecipeController
from cbpi.controller.fermenter_recipe_controller import FermenterRecipeController
from cbpi.controller.upload_controller import UploadController
from cbpi.controller.fermentation_controller import FermentationController

from cbpi.controller.system_controller import SystemController
from cbpi.controller.satellite_controller import SatelliteController

from cbpi.controller.log_file_controller import LogController

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
from cbpi.http_endpoints.http_recipe import RecipeHttpEndpoints
from cbpi.http_endpoints.http_fermenterrecipe import FermenterRecipeHttpEndpoints
from cbpi.http_endpoints.http_plugin import PluginHttpEndpoints
from cbpi.http_endpoints.http_system import SystemHttpEndpoints
from cbpi.http_endpoints.http_log import LogHttpEndpoints
from cbpi.http_endpoints.http_notification import NotificationHttpEndpoints
from cbpi.http_endpoints.http_upload import UploadHttpEndpoints
from cbpi.http_endpoints.http_fermentation import FermentationHttpEndpoints

import shortuuid
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
    except Exception as ex:
        return web.json_response(status=500, data={'error': str(ex)})

    return web.json_response(status=500, data={'error': message})


class CraftBeerPi:

    def __init__(self, configFolder):

        operationsystem= sys.platform
        if operationsystem.startswith('win'):
            set_event_loop_policy(WindowsSelectorEventLoopPolicy())

        self.path = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1])  # The path to the package dir
        
        self.version = __version__
        self.codename = __codename__

        self.config_folder = configFolder
        self.static_config = load_config(configFolder.get_file_path("config.yaml"))
        
        logger.info("Init CraftBeerPI")

        policy = auth.SessionTktAuthentication(urandom(32), 60, include_ip=True)
        middlewares = [web.normalize_path_middleware(), session_middleware(EncryptedCookieStorage(urandom(32))),
                       auth.auth_middleware(policy), error_middleware]
        # max upload size increased to 5 Mb. Default is 1 Mb -> config and svg upload
        self.app = web.Application(middlewares=middlewares, client_max_size=5*1024*1024)
        self.app["cbpi"] = self

        self._setup_shutdownhook()
        self.initializer = []

        self.bus = CBPiEventBus(self.app.loop, self)
        self.job = JobController(self)
        self.config = ConfigController(self)
        self.ws = CBPiWebSocket(self)
        self.actor = ActorController(self)
        self.sensor = SensorController(self)
        self.plugin = PluginController(self)
        self.log = LogController(self)
        self.system = SystemController(self)
        self.kettle = KettleController(self)
        self.fermenter : FermentationController = FermentationController(self)
        self.step : StepController = StepController(self)
        self.recipe : RecipeController = RecipeController(self)
        self.fermenterrecipe : FermenterRecipeController = FermenterRecipeController(self)
        self.upload : UploadController = UploadController(self)
        self.notification : NotificationController = NotificationController(self)
        self.satellite = None
        if str(self.static_config.get("mqtt", False)).lower() == "true":
            self.satellite: SatelliteController = SatelliteController(self)
        self.dashboard = DashboardController(self)

        self.http_step = StepHttpEndpoints(self)
        self.http_recipe = RecipeHttpEndpoints(self)
        self.http_fermenterrecipe = FermenterRecipeHttpEndpoints(self)
        self.http_sensor = SensorHttpEndpoints(self)
        self.http_config = ConfigHttpEndpoints(self)
        self.http_actor = ActorHttpEndpoints(self)
        self.http_kettle = KettleHttpEndpoints(self)
        self.http_dashboard = DashBoardHttpEndpoints(self)
        self.http_plugin = PluginHttpEndpoints(self)
        self.http_system = SystemHttpEndpoints(self)
        self.http_log = LogHttpEndpoints(self)
        self.http_notification = NotificationHttpEndpoints(self)
        self.http_upload = UploadHttpEndpoints(self)
        self.http_fermenter = FermentationHttpEndpoints(self)

        self.login = Login(self)

    def _setup_shutdownhook(self):
        self.shutdown = False

        async def on_cleanup(app):
            self.shutdown = True

        self.app.on_cleanup.append(on_cleanup)

    def register_on_startup(self, obj):

        for method in [getattr(obj, f) for f in dir(obj) if
                       callable(getattr(obj, f)) and hasattr(getattr(obj, f), "on_startup")]:
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
        # self.ws.register_object(obj)
        self.job.register_background_task(obj)
        self.register_on_startup(obj)

    def register_http_endpoints(self, obj, url_prefix=None, static=None):

        if url_prefix is None:
            logger.debug(
                "URL Prefix is None for %s. No endpoints will be registered. Please set / explicit if you want to add it to the root path" % obj)
            return
        routes = []
        for method in [getattr(obj, f) for f in dir(obj) if
                       callable(getattr(obj, f)) and hasattr(getattr(obj, f), "route")]:
            http_method = method.__getattribute__("method")
            path = method.__getattribute__("path")
            class_name = method.__self__.__class__.__name__
            logger.debug(
                "Register Endpoint : %s.%s %s %s%s " % (class_name, method.__name__, http_method, url_prefix, path))

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
            logger.debug("URL Prefix: %s " % (url_prefix,))
            sub = web.Application()
            sub.add_routes(routes)
            if static is not None:
                sub.add_routes([web.static('/static', static, show_index=True)])
            self.app.add_subapp(url_prefix, sub)
        else:

            self.app.add_routes(routes)

    def _swagger_setup(self):
        '''
        Internal method to expose REST API documentation by swagger
        
        :return: 
        '''
        long_description = """
        This is the api for CraftBeerPi
        """
        setup_swagger(self.app,
                      description=long_description,
                      title="CraftBeerPi",
                      api_version=self.version,
                      contact="info@craftbeerpi.com")


    def notify(self, title: str, message: str, type: NotificationType = NotificationType.INFO, action=[]) -> None:
        self.notification.notify(title, message, type, action)
        
    def push_update(self, topic, data, retain=False) -> None:

        if self.satellite is not None:
            asyncio.create_task(self.satellite.publish(topic=topic, message=json.dumps(data), retain=retain))

    async def call_initializer(self, app):
        self.initializer = sorted(self.initializer, key=lambda k: k['order'])
        for i in self.initializer:
            logger.info("CALL INITIALIZER %s - %s " % (i["name"], i["method"].__name__))
            await i["method"]()

    def _print_logo(self):
        from pyfiglet import Figlet
        f = Figlet(font='big')
        logger.info("\n%s" % f.renderText("CraftBeerPi %s " % self.version))
        logger.info("www.CraftBeerPi.com")
        logger.info("(c) 2021/2022 Manuel Fritsch / Alexander Vollkopf")

    def _setup_http_index(self):
        async def http_index(request):
            url = self.config.static.get("index_url")

            if url is not None:

                raise web.HTTPFound(url)
            else:
                return web.Response(text="Hello from CraftbeerPi!")

        self.app.add_routes([web.get('/', http_index),
                             web.static('/static', os.path.join(os.path.dirname(__file__), "static"), show_index=True)])

    async def init_serivces(self):

        self._print_logo()

        await self.job.init()
        
        await self.config.init()
        if self.satellite is not None:
            await self.satellite.init()
        self._setup_http_index()
        self.plugin.load_plugins()
        self.plugin.load_plugins_from_evn()
        await self.fermenter.init()
        await self.sensor.init()
        await self.step.init()
        
        await self.actor.init()
        await self.kettle.init()
        await self.call_initializer(self.app)
        await self.dashboard.init()


        self._swagger_setup()

        return self.app

    def start(self):
        web.run_app(self.init_serivces(), port=self.static_config.get("port", 2202))
