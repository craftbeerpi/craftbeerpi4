
import pandas as pd
import datetime

def dateparse(time_in_secs):
            '''
            Internal helper for date parsing
            :param time_in_secs:
            :return:
            '''
            return datetime.datetime.strptime(time_in_secs, '%Y-%m-%d %H:%M:%S')

df = pd.read_csv("./logs/sensor_JUGteK9KrSVPDxboWjBS4N.log", parse_dates=True, date_parser=dateparse, index_col='DateTime', names=['DateTime',"Values"], header=None) 
print({"JUGteK9KrSVPDxboWjBS4N": {"time": df.index.astype(str).tolist(), "value":df.Values.tolist()}})
