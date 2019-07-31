# -*- coding: utf-8 -*-
import asyncio
from aiohttp import web
from cbpi.api import *

import re

class CustomSensor(CBPiSensor):

    # Custom Properties which will can be configured by the user

    p1 = Property.Number(label="Test")
    p2 = Property.Text(label="Test")
    interval = Property.Number(label="interval", configurable=True)

    # Internal runtime variable
    value = 0

    @action(key="name", parameters={})
    def myAction(self):
        '''
        Custom Action Exampel
        :return: None
        '''
        pass

    def init(self):
        super().init()
        self.state = True

    def get_state(self):
        return self.state



    def get_value(self):

        return self.value

    def get_unit(self):
        return "°%s" % self.get_parameter("TEMP_UNIT", "C")

    def stop(self):
        pass

    async def run(self, cbpi):
        self.value = 0
        while True:
            await asyncio.sleep(self.interval)
            self.value = self.value + 1
            self.log_data(self.value)
            await cbpi.bus.fire("sensor/%s/data" % self.id, value=self.value)

cache = {}


class HTTPSensor(CBPiSensor):

    # Custom Properties which will can be configured by the user

    key = Property.Text(label="Key", configurable=True)

    def init(self):
        super().init()

        self.state = True

    def get_state(self):
        return self.state

    def get_value(self):

        return self.value

    def stop(self):
        pass

    async def run(self, cbpi):
        self.value = 0
        while True:
            await asyncio.sleep(1)

            try:
                value = cache.pop(self.key, None)

                if value is not None:
                    self.log_data(value)
                    await cbpi.bus.fire("sensor/%s/data" % self.id, value=value)
            except Exception as e:
                print(e)
                pass

class HTTPSensorEndpoint(CBPiExtension):


    def __init__(self, cbpi):
        '''
        Initializer

        :param cbpi:
        '''
        self.pattern_check = re.compile("^[a-zA-Z0-9,.]{0,10}$")

        self.cbpi = cbpi
        # register component for http, events
        # In addtion the sub folder static is exposed to access static content via http
        self.cbpi.register(self, "/httpsensor")


    @request_mapping(path="/{key}/{value}", auth_required=False)
    async def http_new_value2(self, request):
        """
        ---
        description: Kettle Heater on
        tags:
        - HttpSensor
        parameters:
        - name: "key"
          in: "path"
          description: "Sensor Key"
          required: true
          type: "string"
        - name: "value"
          in: "path"
          description: "Value"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
        """

        global cache
        key = request.match_info['key']
        value = request.match_info['value']
        if self.pattern_check.match(key) is None:
            return web.json_response(status=422, data={'error': "Key not matching pattern ^[a-zA-Z0-9,.]{0,10}$"})

        if self.pattern_check.match(value) is None:
            return web.json_response(status=422, data={'error': "Data not matching pattern ^[a-zA-Z0-9,.]{0,10}$"})

        print("HTTP SENSOR ", key, value)
        cache[key] = value

        return web.Response(status=204)


def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''
    cbpi.plugin.register("HTTPSensor", HTTPSensor)
    cbpi.plugin.register("HTTPSensorEndpoint", HTTPSensorEndpoint)
    cbpi.plugin.register("CustomSensor", CustomSensor)
