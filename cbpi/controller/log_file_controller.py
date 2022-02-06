import datetime
import glob
import logging
import os
from logging.handlers import RotatingFileHandler
from time import strftime, localtime
import pandas as pd
import zipfile
import base64
import urllib3
from cbpi.api import *
from cbpi.api.config import ConfigType
from cbpi.api.base import CBPiBase
import asyncio


class LogController:

    def __init__(self, cbpi):
        '''

        :param cbpi: craftbeerpi object
        '''
        self.cbpi = cbpi
        self.logger = logging.getLogger(__name__)
        self.configuration = False
        self.datalogger = {}

#        self.cbpi.config.get does not seem to work here...
#        self.influxdbaddr="192.168.163.105"
#        self.influxdbport="8086"
#        self.influxdbname="cbpi4"
#        self.influxdburl='http://' + self.influxdbaddr + ':' + str(self.influxdbport) + '/write?db=' + self.influxdbname
#        self.influxdbuser=""
#        self.influxdbpwd=""
#        self.base64string = base64.b64encode(('%s:%s' % (self.influxdbuser,self.influxdbpwd)).encode())

    def log_data(self, name: str, value: str) -> None:
        self.logfiles = self.cbpi.config.get("CSVLOGFILES", "Yes")
        self.influxdb = self.cbpi.config.get("INFLUXDB", "No")
        if self.logfiles == "Yes":
            if name not in self.datalogger:
                max_bytes = self.cbpi.config.get("SENSOR_LOG_MAX_BYTES", 1048576)
                backup_count = self.cbpi.config.get("SENSOR_LOG_BACKUP_COUNT", 3)
    
                data_logger = logging.getLogger('cbpi.sensor.%s' % name)
                data_logger.propagate = False
                data_logger.setLevel(logging.DEBUG)
                handler = RotatingFileHandler('./logs/sensor_%s.log' % name, maxBytes=max_bytes, backupCount=backup_count)
                data_logger.addHandler(handler)
                self.datalogger[name] = data_logger

            formatted_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
            self.datalogger[name].info("%s,%s" % (formatted_time, value))

        if self.influxdb == "Yes":
            self.influxdbcloud = self.cbpi.config.get("INFLUXDBCLOUD", "No")
            self.influxdbaddr = self.cbpi.config.get("INFLUXDBADDR", None)
            self.influxdbport = self.cbpi.config.get("INFLUXDBPORT", None)
            self.influxdbname = self.cbpi.config.get("INFLUXDBNAME", None)
            self.influxdbuser = self.cbpi.config.get("INFLUXDBUSER", None)
            self.influxdbpwd = self.cbpi.config.get("INFLUXDBPWD", None)
            
            id = name
            try:
                chars = {'ö':'oe','ä':'ae','ü':'ue','Ö':'Oe','Ä':'Ae','Ü':'Ue'}
                sensor=self.cbpi.sensor.find_by_id(name)
                if sensor is not None:
                    itemname=sensor.name.replace(" ", "_")
                    for char in chars:
                        itemname = itemname.replace(char,chars[char])
                    out="measurement,source=" + itemname + ",itemID=" + str(id) + " value="+str(value)
            except Exception as e:
                logging.error("InfluxDB ID Error: {}".format(e))

            if self.influxdbcloud == "Yes":
                self.influxdburl="https://" + self.influxdbaddr + "/api/v2/write?org=" + self.influxdbuser + "&bucket=" + self.influxdbname + "&precision=s"
                try:
                    header = {'User-Agent': name, 'Authorization': "Token {}".format(self.influxdbpwd)}
                    http = urllib3.PoolManager()
                    req = http.request('POST',self.influxdburl, body=out, headers = header)
                except Exception as e:
                    logging.error("InfluxDB cloud write Error: {}".format(e))

            else:
                self.influxdb = self.cbpi.config.get("INFLUXDB", "No")
                self.base64string = base64.b64encode(('%s:%s' % (self.influxdbuser,self.influxdbpwd)).encode())
                self.influxdburl='http://' + self.influxdbaddr + ':' + str(self.influxdbport) + '/write?db=' + self.influxdbname

                try:
                    header = {'User-Agent': name, 'Content-Type': 'application/x-www-form-urlencoded','Authorization': 'Basic %s' % self.base64string.decode('utf-8')}
                    http = urllib3.PoolManager()
                    req = http.request('POST',self.influxdburl, body=out, headers = header)
                except Exception as e:
                    logging.error("InfluxDB write Error: {}".format(e))



    async def get_data(self, names, sample_rate='60s'):
        logging.info("Start Log for {}".format(names))
        '''
        :param names: name as string or list of names as string
        :param sample_rate: rate for resampling the data
        :return:
        '''
        # make string to array
        if isinstance(names, list) is False:
            names = [names]

        # remove duplicates
        names = set(names)

        
        result = None

        def dateparse(time_in_secs):
            '''
            Internal helper for date parsing
            :param time_in_secs:
            :return:
            '''
            return datetime.datetime.strptime(time_in_secs, '%Y-%m-%d %H:%M:%S')

        def datetime_to_str(o):
            if isinstance(o, datetime.datetime):
                return o.__str__()

        for name in names:
            # get all log names
            all_filenames = glob.glob('./logs/sensor_%s.log*' % name)

            # concat all logs
            df = pd.concat([pd.read_csv(f, parse_dates=True, date_parser=dateparse, index_col='DateTime', names=['DateTime', name], header=None) for f in all_filenames])
            logging.info("Read all files for {}".format(names))
            # resample if rate provided
            if sample_rate is not None:
                df = df[name].resample(sample_rate).max()
            logging.info("Sampled now for {}".format(names))
            df = df.dropna()
            if result is None:
                result = df
            else:
                result = pd.merge(result, df, how='outer', left_index=True, right_index=True)

        data = {"time": df.index.tolist()}

        if len(names) > 1:
            for name in names:
                data[name] = result[name].interpolate(limit_direction='both', limit=10).tolist()
        else:
            data[name] = result.interpolate().tolist()
        logging.info("Send Log for {}".format(names))
        return data

    async def get_data2(self, ids) -> dict:
        def dateparse(time_in_secs):
            return datetime.datetime.strptime(time_in_secs, '%Y-%m-%d %H:%M:%S')
        
        result = dict()
        for id in ids:
            df = pd.read_csv("./logs/sensor_%s.log" % id, parse_dates=True, date_parser=dateparse, index_col='DateTime', names=['DateTime',"Values"], header=None) 
            result[id] = {"time": df.index.astype(str).tolist(), "value":df.Values.tolist()}
        return result



    def get_logfile_names(self, name:str ) -> list:
        '''
        Get all log file names
        :param name: log name as string. pattern /logs/sensor_%s.log*
        :return: list of log file names
        '''

        return [os.path.basename(x) for x in glob.glob('./logs/sensor_%s.log*' % name)]

    def clear_log(self, name:str ) -> str:
        
        all_filenames = glob.glob('./logs/sensor_%s.log*' % name)
        for f in all_filenames:
            os.remove(f)

        if name in self.datalogger:
            del self.datalogger[name]


    def get_all_zip_file_names(self, name: str) -> list:

        '''
        Return a list of all zip file names
        :param name: 
        :return: 
        '''

        return [os.path.basename(x) for x in glob.glob('./logs/*-sensor-%s.zip' % name)]

    def clear_zip(self, name:str ) -> None:
        """
        clear all zip files for a sensor
        :param name: sensor name
        :return: None
        """

        all_filenames = glob.glob('./logs/*-sensor-%s.zip' % name)
        for f in all_filenames:
            os.remove(f)

    def zip_log_data(self, name: str) -> str:
        """
        :param name: sensor name
        :return: zip_file_name
        """

        formatted_time = strftime("%Y-%m-%d-%H_%M_%S", localtime())
        file_name = './logs/%s-sensor-%s.zip' % (formatted_time, name)
        zip = zipfile.ZipFile(file_name, 'w', zipfile.ZIP_DEFLATED)
        all_filenames = glob.glob('./logs/sensor_%s.log*' % name)
        for f in all_filenames:
            zip.write(os.path.join(f))
        zip.close()
        return os.path.basename(file_name)


