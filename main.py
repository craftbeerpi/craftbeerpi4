import aiosqlite
from aiohttp import web
from aiohttp_swagger import *
from aiojobs.aiohttp import setup, spawn, get_scheduler_from_app
from core.matcher import MQTTMatcher
from hbmqtt.broker import Broker
from hbmqtt.client import MQTTClient
from hbmqtt.mqtt.constants import QOS_1

from core.websocket import websocket_handler

TEST_DB = "test.db"
c = MQTTClient()
import asyncio

matcher = MQTTMatcher()

config = {
    'listeners': {
        'default': {
            'type': 'tcp',
            'bind': '0.0.0.0:1885',
        },
        'my-ws-1': {
            'bind': '0.0.0.0:8888',
            'type': 'ws'
        }
    },

    'sys_interval': 10,
    'auth': {
        'allow-anonymous': True,
    }
}

broker = Broker(config, plugin_namespace="hbmqtt.test.plugins")


async def test2(name):
    while True:
        print(name)
        await asyncio.sleep(1)





async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = "Hello, " + name

    return web.Response(text=text)


async def test_connection():
    async with aiosqlite.connect(TEST_DB) as db:

        assert isinstance(db, aiosqlite.Connection)


app = web.Application()


async def listen_to_redis(app):
    while True:
        await asyncio.sleep(1)

        #for w in _ws:
        #    pass
            # await w.send_str("HALLO")

            # print(w)


async def myjob(app):
    while True:
        await asyncio.sleep(1)



def ok_msg(msg):
    pass


def ok_msg1(msg):
    pass


def ok_msg2(msg):
    pass


mqtt_methods = {"test": ok_msg, "test/+/ab": ok_msg1, "test/+": ok_msg2}


async def on_message():
    while True:
        message = await c.deliver_message()
        matched = False
        packet = message.publish_packet
        print(message.topic)
        print(message.topic.split('/'))
        data = packet.payload.data.decode("utf-8")

        for callback in matcher.iter_match(message.topic):

            callback(data)
            matched = True

        if matched == False:
            print("NO HANDLER", data)

        #for w in _ws:
        #    await w.send_str(data)


async def start_background_tasks(app):
    app['redis_listener'] = app.loop.create_task(listen_to_redis(app))


async def start_broker(app):

    await broker.start()

    await c.connect('mqtt://localhost:1885')

    for k, v in mqtt_methods.items():
        print(k, v)
        await c.subscribe([(k, QOS_1)])

        matcher[k] = v
    # await c.subscribe([('/test', QOS_1),('/hallo', QOS_1)])


    await get_scheduler_from_app(app).spawn(on_message())


job = None


async def start_task(request):
    global job
    job = await spawn(request, myjob(app))
    await test_connection()
    return web.Response(text="OK")


async def stop_task(request):
    await job.close()
    return web.Response(text="OK")


async def stats(request):
    s = get_scheduler_from_app(app)

    return web.Response(text="%s" % s.active_count)





setup(app)


def start_bg(app, name, method):
    print("HALLO111")

    async def start(app):
        app[name] = app.loop.create_task(method(name))

    app.on_startup.append(start)


# start_bg(app, "test", test2)
# start_bg(app, "test2", test2)

#app.on_startup.append(start_background_tasks)
app.on_startup.append(start_broker)

app.add_routes([web.get('/', handle),
                web.get('/stop', stop_task),
                web.get('/start', start_task),
                web.get('/stats', stats),
                web.get('/ws', websocket_handler),
                web.get('/{name}', handle)

                ])

setup_swagger(app)

web.run_app(app)
