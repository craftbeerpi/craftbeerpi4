import asyncio
import logging
from os import urandom
import os

import yaml
from aiohttp import web
from aiohttp_auth import auth
from aiohttp_session import session_middleware
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from aiohttp_swagger import setup_swagger

from core.controller.config_controller import ConfigController
from core.controller.kettle_controller import KettleController
from core.controller.step_controller import StepController
from core.extension.comp import MyComp
from core.job.aiohttp import setup, get_scheduler_from_app

from core.controller.actor_controller import ActorController
from core.controller.notification_controller import NotificationController
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


"""
This is a module docstring
"""

class CraftBeerPi():
    """
    This is a Hello class docstring
    """

    def __init__(self):
        this_directory = os.path.dirname(__file__)

        self.config = load_config(os.path.join(this_directory, '../config/config.yaml'))

        logger.info("Init CraftBeerPI")
        policy = auth.SessionTktAuthentication(urandom(32), 60, include_ip=True)
        middlewares = [session_middleware(EncryptedCookieStorage(urandom(32))), auth.auth_middleware(policy)]
        self.app = web.Application(middlewares=middlewares)
        self.initializer = []

        setup(self.app, self)
        self.bus = EventBus(self.app.loop, self)
        self.ws = WebSocket(self)
        self.actor = ActorController(self)
        self.sensor = SensorController(self)
        self.plugin = PluginController(self)
        self.system = SystemController(self)
        self.config2 = ConfigController(self)
        self.kettle = KettleController(self)
        self.step = StepController(self)
        self.notification = NotificationController(self)
        #self.dummy = MyComp(self)


        self.login = Login(self)

        self.plugin.load_plugins()
        self.register_events(self.ws)


    def register_events(self, obj):

        for method in [getattr(obj, f) for f in dir(obj) if callable(getattr(obj, f)) and hasattr(getattr(obj, f), "eventbus")]:

            doc = None
            if method.__doc__ is not None:
                try:
                    doc = yaml.load(method.__doc__)
                    doc["topic"] = method.__getattribute__("topic")
                except:
                    pass
            self.bus.register(method.__getattribute__("topic"), method)

    def register_background_task(self, obj):
        '''
        This method parses all method for the @background_task decorator and registers the background job
        which will be launched during start up of the server
        
        :param obj: the object to parse
        :return: 
        '''

        async def job_loop(app, name, interval, method):
            logger.info("Start Background Task %s Interval %s Method %s" % (name, interval, method))
            while True:
                logger.debug("Execute Task %s - interval(%s second(s)" % (name, interval))
                await asyncio.sleep(interval)
                await method()

        async def spawn_job(app):
            scheduler = get_scheduler_from_app(self.app)
            for method in [getattr(obj, f) for f in dir(obj) if callable(getattr(obj, f)) and hasattr(getattr(obj, f), "background_task")]:
                name = method.__getattribute__("name")
                interval = method.__getattribute__("interval")
                job = await scheduler.spawn(job_loop(self.app, name, interval, method),name, "background")


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

    def register(self, obj, url_prefix=None, static=None):

        '''
        This method parses the provided object
        
        :param obj: the object wich will be parsed for registration 
        :param url_prefix: that prefix for HTTP Endpoints
        :return: None
        '''
        self.register_http_endpoints(obj, url_prefix, static)
        self.register_events(obj)
        self.register_ws(obj)
        self.register_background_task(obj)
        self.register_on_startup(obj)

    def register_http_endpoints(self, obj, url_prefix=None, static=None):
        '''
        This method parses the provided object for @request_mapping decorator
        
        :param obj: the object which will be analyzed 
        :param url_prefix: the prefix which will be used for the all http endpoints of the object
        :return: 
        '''
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
            print("Prefx", url_prefix)
            sub = web.Application()
            sub.add_routes(routes)
            if static is not None:
                sub.add_routes([web.static('/static', static, show_index=True)])
            self.app.add_subapp(url_prefix, sub)
        else:
            self.app.add_routes(routes)


    async def start_job(self, method, name, type):
        scheduler = get_scheduler_from_app(self.app)
        return await scheduler.spawn(method, name, type)

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
                      title=self.config.get("name", "CraftBeerPi"),
                      api_version=self.config.get("version", ""),
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


    def setup(self):
        '''
        This method will start the server
        
        :return: 
        '''

        print("INIT CONTROLLER")

        from pyfiglet import Figlet
        f = Figlet(font='big')
        print(f.renderText("%s %s" % (self.config.get("name"), self.config.get("version"))))

        async def init_database(app):
            await DBModel.test_connection()

        async def init_controller(app):
            await self.sensor.init()
            await self.step.init()
            await self.actor.init()
            await self.kettle.init()

            import pprint
            pprint.pprint(self.bus.dump())


        async def load_plugins(app):
            #await PluginController.load_plugin_list()
            #self.plugin.load_plugins()
            pass

        async def call_initializer(app):

            self.initializer = sorted(self.initializer, key=lambda k: k['order'])
            for i in self.initializer:
                logger.info("CALL INITIALIZER %s - %s " % (i["name"], i["method"].__name__))

                await i["method"]()


        self.app.on_startup.append(init_database)
        self.app.on_startup.append(call_initializer)

        self.app.on_startup.append(load_plugins)
        self.app.on_startup.append(init_controller)

        self._swagger_setup()

    def start(self):
        web.run_app(self.app, port=self.config.get("port", 8080))
