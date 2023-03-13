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
from pathlib import Path
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
        self.logsFolderPath = self.cbpi.config_folder.logsFolderPath
        self.logger.info("Log folder path  : " + self.logsFolderPath)

    def log_data(self, name: str, value: str) -> None:
        self.logfiles = self.cbpi.config.get("CSVLOGFILES", "Yes")
        self.influxdb = self.cbpi.config.get("INFLUXDB", "No")
        if self.logfiles == "Yes":
            if name not in self.datalogger:
                max_bytes = int(self.cbpi.config.get("SENSOR_LOG_MAX_BYTES", 100000))
                backup_count = int(self.cbpi.config.get("SENSOR_LOG_BACKUP_COUNT", 3))
    
                data_logger = logging.getLogger('cbpi.sensor.%s' % name)
                data_logger.propagate = False
                data_logger.setLevel(logging.DEBUG)
                handler = RotatingFileHandler(os.path.join(self.logsFolderPath, f"sensor_{name}.log"), maxBytes=max_bytes, backupCount=backup_count)
                data_logger.addHandler(handler)
                self.datalogger[name] = data_logger

            formatted_time = strftime("%Y-%m-%d %H:%M:%S", localtime())
            self.datalogger[name].info("%s,%s" % (formatted_time, str(value)))
        if self.influxdb == "Yes":
            self.influxdbcloud = self.cbpi.config.get("INFLUXDBCLOUD", "No")
            self.influxdbaddr = self.cbpi.config.get("INFLUXDBADDR", None)
            #self.influxdbport = self.cbpi.config.get("INFLUXDBPORT", None)
            self.influxdbname = self.cbpi.config.get("INFLUXDBNAME", None)
            self.influxdbuser = self.cbpi.config.get("INFLUXDBUSER", None)
            self.influxdbpwd = self.cbpi.config.get("INFLUXDBPWD", None)
            self.influxdbmeasurement = self.cbpi.config.get("INFLUXDBMEASUREMENT", "measurement")
            
            id = name
            try:
                chars = {'ö':'oe','ä':'ae','ü':'ue','Ö':'Oe','Ä':'Ae','Ü':'Ue'}
                sensor=self.cbpi.sensor.find_by_id(name)
                if sensor is not None:
                    itemname=sensor.name.replace(" ", "_")
                    for char in chars:
                        itemname = itemname.replace(char,chars[char])
                    out=str(self.influxdbmeasurement)+",source=" + itemname + ",itemID=" + str(id) + " value="+str(value)
            except Exception as e:
                logging.error("InfluxDB ID Error: {}".format(e))

            if self.influxdbcloud == "Yes":
                self.influxdburl=self.influxdbaddr + "/api/v2/write?org=" + self.influxdbuser + "&bucket=" + self.influxdbname + "&precision=s"
                try:
                    header = {'User-Agent': name, 'Authorization': "Token {}".format(self.influxdbpwd)}
                    http = urllib3.PoolManager()
                    req = http.request('POST',self.influxdburl, body=out, headers = header)
                except Exception as e:
                    logging.error("InfluxDB cloud write Error: {}".format(e))

            else:
                self.base64string = base64.b64encode(('%s:%s' % (self.influxdbuser,self.influxdbpwd)).encode())
                self.influxdburl= self.influxdbaddr + '/write?db=' + self.influxdbname
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
            all_filenames = glob.glob(os.path.join(self.logsFolderPath, f"sensor_{name}.log*"))
            # concat all logs
            df = pd.concat([pd.read_csv(f, parse_dates=True, date_parser=dateparse, index_col='DateTime', names=['DateTime', name], header=None) for f in all_filenames])
            logging.info("Read all files for {}".format(names))
            # resample if rate provided
            if sample_rate is not None:
                df = df[name].resample(sample_rate).max()
            logging.info("Sampled now for {}".format(names))
            df = df.dropna()
            # take every nth row so that total number of rows does not exceed max_rows * 2
            max_rows = 500
            total_rows = df.shape[0]
            if (total_rows > 0) and (total_rows > max_rows):
                nth = int(total_rows/max_rows)
                if nth > 1:
                    df = df.iloc[::nth]
                    
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
        
        dateparse = lambda dates: [datetime.datetime.strptime(d, '%Y-%m-%d %H:%M:%S') for d in dates]       
        result = dict()
        for id in ids:
            try:
                all_filenames = glob.glob(os.path.join(self.logsFolderPath,f"sensor_{id}.log*"))
                df = pd.concat([pd.read_csv(f, parse_dates=['DateTime'], date_parser=dateparse, index_col='DateTime', names=['DateTime', 'Values'], header=None) for f in all_filenames])
                df = df.resample('60s').max()
                df = df.dropna()
                result[id] = {"time": df.index.astype(str).tolist(), "value":df.Values.tolist()}
            except:
                pass
        return result



    def get_logfile_names(self, name:str ) -> list:
        '''
        Get all log file names
        :param name: log name as string. pattern /logs/sensor_%s.log*
        :return: list of log file names
        '''

        return [os.path.basename(x) for x in glob.glob(os.path.join(self.logsFolderPath, f"sensor_{name}.log*"))]

    def clear_log(self, name:str ) -> str:
        all_filenames = glob.glob(os.path.join(self.logsFolderPath, f"sensor_{name}.log*"))

        if name in self.datalogger:
            self.datalogger[name].removeHandler(self.datalogger[name].handlers[0])
            del self.datalogger[name]

        for f in all_filenames:
            try:
                os.remove(f)
            except Exception as e:
                logging.warning(e)



    def get_all_zip_file_names(self, name: str) -> list:

        '''
        Return a list of all zip file names
        :param name: 
        :return: 
        '''

        return [os.path.basename(x) for x in glob.glob(os.path.join(self.logsFolderPath, f"*-sensor-{name}.zip"))]

    def clear_zip(self, name:str ) -> None:
        """
        clear all zip files for a sensor
        :param name: sensor name
        :return: None
        """

        all_filenames = glob.glob(os.path.join(self.logsFolderPath, f"*-sensor-{name}.zip"))
        for f in all_filenames:
            os.remove(f)

    def zip_log_data(self, name: str) -> str:
        """
        :param name: sensor name
        :return: zip_file_name
        """

        formatted_time = strftime("%Y-%m-%d-%H_%M_%S", localtime())
        file_name = os.path.join(self.logsFolderPath, f"{formatted_time}-sensor-{name}.zip")
        zip = zipfile.ZipFile(file_name, 'w', zipfile.ZIP_DEFLATED)
        all_filenames = glob.glob(os.path.join(self.logsFolderPath, f"sensor_{name}.log*"))
        for f in all_filenames:
            zip.write(os.path.join(f))
        zip.close()
        return os.path.basename(file_name)


