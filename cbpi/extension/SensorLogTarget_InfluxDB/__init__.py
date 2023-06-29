
# -*- coding: utf-8 -*-
import os
from urllib3 import Timeout, PoolManager, Retry
import logging
from unittest.mock import MagicMock, patch
import asyncio
import random
from cbpi.api import *
from cbpi.api.config import ConfigType
import urllib3
import base64

logger = logging.getLogger(__name__)

class SensorLogTargetInfluxDB(CBPiExtension):

    def __init__(self, cbpi): # called from cbpi on start
        self.cbpi = cbpi
        self.influxdb = self.cbpi.config.get("INFLUXDB", "No")
        if self.influxdb == "No":
            return # never run()
        self._task = asyncio.create_task(self.run()) # one time run() only
        self.counter = 0
        self.max_retries = 2
        self.send=True


    async def run(self): # called by __init__ once on start if influx is enabled
        self.listener_ID = self.cbpi.log.add_sensor_data_listener(self.log_data_to_InfluxDB)
        logger.info("InfluxDB sensor log target listener ID: {}".format(self.listener_ID))

    async def log_data_to_InfluxDB(self, cbpi, id:str, value:str, timestamp, name): # called by log_data() hook from the log file controller
        self.influxdb = self.cbpi.config.get("INFLUXDB", "No")
        if self.influxdb == "No":
            # We intentionally do not unsubscribe the listener here because then we had no way of resubscribing him without a restart of cbpi
            # as long as cbpi was STARTED with INFLUXDB set to Yes this function is still subscribed, so changes can be made on the fly.
            # but after initially enabling this logging target a restart is required.
            return
        self.influxdbcloud = self.cbpi.config.get("INFLUXDBCLOUD", "No")
        self.influxdbaddr = self.cbpi.config.get("INFLUXDBADDR", None)
        self.influxdbname = self.cbpi.config.get("INFLUXDBNAME", None)
        self.influxdbuser = self.cbpi.config.get("INFLUXDBUSER", None)
        self.influxdbpwd = self.cbpi.config.get("INFLUXDBPWD", None)
        self.influxdbmeasurement = self.cbpi.config.get("INFLUXDBMEASUREMENT", "measurement")
        timeout = Timeout(connect=2.0, read=None)
        try:
            sensor=self.cbpi.sensor.find_by_id(id)
            if sensor is not None:
                itemname=sensor.name.replace(" ", "_")
                out=str(self.influxdbmeasurement)+",source=" + itemname + ",itemID=" + str(id) + " value="+str(value)
        except Exception as e:
            logging.error("InfluxDB ID Error: {}".format(e))

        if self.influxdbcloud == "Yes" and self.send == True:
            if self.counter <= self.max_retries:
                self.influxdburl=self.influxdbaddr + "/api/v2/write?org=" + self.influxdbuser + "&bucket=" + self.influxdbname + "&precision=s"
                try:
                    header = {'User-Agent': id, 'Authorization': "Token {}".format(self.influxdbpwd)}
                    http = PoolManager(timeout=timeout)
                    req = http.request('POST',self.influxdburl, body=out.encode(), headers = header, retries=Retry(2))
                    if req.status != 204:
                        raise Exception(f'InfluxDB Status code {req.status}')
                except Exception as e:
                    self.counter += 1
                    logging.error("InfluxDB cloud write Error #{}: {}".format(self.counter, e))
            else:
                logging.warning("Waiting 3 Minutes before connecting to INFLUXDB again")
                self.send=False
                await asyncio.sleep(180)
                self.counter = 0
                self.send = True

        elif self.influxdbcloud == "No" and self.send == True:
            if self.counter <= self.max_retries:
                self.base64string = base64.b64encode(('%s:%s' % (self.influxdbuser,self.influxdbpwd)).encode())
                self.influxdburl= self.influxdbaddr + '/write?db=' + self.influxdbname
                try:
                    header = {'User-Agent': id, 'Content-Type': 'application/x-www-form-urlencoded','Authorization': 'Basic %s' % self.base64string.decode('utf-8')}
                    http = PoolManager(timeout=timeout)
                    req = http.request('POST',self.influxdburl, body=out.encode(), headers = header, retries=Retry(2))
                    if req.status != 204:
                        raise Exception(f'InfluxDB Status code {req.status}')
                except Exception as e:
                    self.counter += 1
                    logging.error("InfluxDB write Error #{}: {}".format(self.counter, e))
            else:
                logging.warning("Waiting 3 Minutes before connecting to INFLUXDB again")
                self.send=False
                await asyncio.sleep(180)
                self.counter = 0
                self.send = True


def setup(cbpi):
    cbpi.plugin.register("SensorLogTargetInfluxDB", SensorLogTargetInfluxDB)
