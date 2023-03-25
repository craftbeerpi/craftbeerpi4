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
             Property.Number(label="Timeout", configurable="True",unit="sec",description="Timeout in seconds to send notification (default:60 | deactivated: 0)"),
             Property.Kettle(label="Kettle", description="Reduced logging if Kettle is inactive (only Kettle or Fermenter to be selected)"),
             Property.Fermenter(label="Fermenter", description="Reduced logging in seconds if Fermenter is inactive (only Kettle or Fermenter to be selected)"),
             Property.Number(label="ReducedLogging", configurable=True, description="Reduced logging frequency in seconds if selected Kettle or Fermenter is inactive (default is 60 sec)")])

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

        self.lastlog=0
        self.reducedfrequency=int(self.props.get("ReducedLogging", 60))
        
        self.kettleid=self.props.get("Kettle", None)
        self.fermenterid=self.props.get("Fermenter", None)
        self.reducedlogging = True if self.kettleid or self.fermenterid else False

        if self.kettleid is not None and self.fermenterid is not None:
            self.reducedlogging=False
            self.cbpi.notify("HTTPSensor", "Sensor '" + str(self.sensor.name) + "' cant't have Fermenter and Kettle defined for reduced logging.", NotificationType.WARNING, action=[NotificationAction("OK", self.Confirm)])

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
            self.kettle = self.get_kettle(self.kettleid) if self.kettleid is not None else None 
            self.fermenter = self.get_fermenter(self.fermenterid) if self.fermenterid is not None else None
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

                    if self.reducedlogging:
                        await self.logvalue()
                    else:
                        self.log_data(self.value)
                        self.lastlog = time.time()

                    if self.timeout !=0:
                        self.nextchecktime = currenttime + self.timeout
                        self.notificationsend = False
                        self.lastdata=time.time()
            except Exception as e:
                logging.error(e)
                pass
            await asyncio.sleep(1)

    async def logvalue(self):
        now=time.time()            
        if self.kettle is not None:
            try:
                kettlestatus=self.kettle.instance.state
            except:
                kettlestatus=False
            if kettlestatus:
                self.log_data(self.value)
                logging.info("Kettle Active")
                self.lastlog = time.time()
            else:
                logging.info("Kettle Inactive")
                if now >= self.lastlog + self.reducedfrequency:
                    self.log_data(self.value)
                    self.lastlog = time.time()
                    logging.info("Logged with reduced freqency")
                    pass   

        if self.fermenter is not None:
            try:
                fermenterstatus=self.fermenter.instance.state
            except:
                fermenterstatus=False
            if fermenterstatus:
                self.log_data(self.value)
                logging.info("Fermenter Active")
                self.lastlog = time.time()
            else:
                logging.info("Fermenter Inactive")
                if now >= self.lastlog + self.reducedfrequency:
                    self.log_data(self.value)
                    self.lastlog = time.time()
                    logging.info("Logged with reduced freqency")
                    pass            

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

