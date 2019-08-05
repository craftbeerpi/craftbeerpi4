import datetime
import glob
import logging
import os
from logging.handlers import RotatingFileHandler
from time import strftime, localtime
import pandas as pd

class LogController:

    def __init__(self, cbpi):
        '''

        :param cbpi: craftbeerpi object
        '''
        self.cbpi = cbpi
        self.logger = logging.getLogger(__name__)

        self.datalogger = {}

    def log_data(self, name: str, value: str) -> None:

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

    async def get_data(self, names, sample_rate='60s'):

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

            # resample if rate provided
            if sample_rate is not None:
                df = df[name].resample(sample_rate).max()

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
        return data


    def get_logfile_names(self, name:str ) -> list:
        '''
        Get all log file names
        :param name: log name as string. pattern /logs/sensor_%s.log*
        :return: list of log file names
        '''
        return = glob.glob('./logs/sensor_%s.log*' % name)

    async def clear_log(self, name:str ) -> str:
        '''

        :param name: log name as string. pattern /logs/sensor_%s.log*
        :return: None
        '''
        all_filenames = glob.glob('./logs/sensor_%s.log*' % name)
        for f in all_filenames:
            print(f)
            os.remove(f)

        if name in self.datalogger:
            del self.datalogger[name]




