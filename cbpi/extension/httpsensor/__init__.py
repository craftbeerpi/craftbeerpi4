# -*- coding: utf-8 -*-
import asyncio
from aiohttp import web
from cbpi.api import *
import time
from datetime import datetime
import re
import logging
from cbpi.api.dataclasses import NotificationAction, NotificationType

cache = {}

@parameters([Property.Text(label="Key", configurable=True, description="Http Key"),
             Property.Number(label="Timeout", configurable="True",unit="sec",description="Timeout in seconds to send notification (default:60 | deactivated: 0)")
])
class HTTPSensor(CBPiSensor):
    def __init__(self, cbpi, id, props):
        super(HTTPSensor, self).__init__(cbpi, id, props)
        self.running = True
        self.value = 0
        self.timeout=int(self.props.get("Timeout", 60))
        self.starttime = time.time()
        self.notificationsend = False
        self.nextchecktime=self.starttime+self.timeout
        self.sensor=self.get_sensor(self.id)
        self.lastdata=time.time()

    async def Confirm(self, **kwargs):
        self.nextchecktime = time.time() + self.timeout
        self.notificationsend = False
        pass

    async def message(self):
        target_timestring= datetime.fromtimestamp(self.lastdata)
        self.cbpi.notify("HTTPSensor Timeout", "Sensor '" + str(self.sensor.name) + "' did not respond.  Last data received: "+target_timestring.strftime("%D %H:%M"), NotificationType.WARNING, action=[NotificationAction("OK", self.Confirm)])
        pass

    async def run(self):
        '''
        This method is executed asynchronousely 
        In this example the code is executed every second
        '''
        while self.running is True:
            if self.timeout !=0:
                currenttime=time.time()            
                if currenttime > self.nextchecktime and self.notificationsend == False:   
                    await self.message()
                    self.notificationsend=True
            try:
                cache_value = cache.pop(self.props.get("Key"), None)
                if cache_value is not None:
                    self.value = float(cache_value)
                    self.push_update(self.value)
                    if self.timeout !=0:
                        self.nextchecktime = currenttime + self.timeout
                        self.notificationsend = False
                        self.lastdata=time.time()
            except Exception as e:
                logging.error(e)
                pass
            await asyncio.sleep(1)

    def get_state(self):
        # return the current state of the sensor
        return dict(value=self.value)

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

