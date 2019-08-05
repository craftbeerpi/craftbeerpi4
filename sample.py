import datetime
import glob
import json
import logging
from logging.handlers import RotatingFileHandler
from time import strftime, localtime
import pandas as pd
import matplotlib.pyplot as plt

sid = 2


data_logger = logging.getLogger('cbpi.sensor.%s' % sid)
data_logger.propagate = False
data_logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler('./logs/sensor_%s.log' % sid, maxBytes=100_000, backupCount=10)
data_logger.addHandler(handler)
import random

start = datetime.datetime.now()
'''
v = random.randint(50,60)
for i in range(5760):
    d = start + datetime.timedelta(seconds=6*i)
    formatted_time = d.strftime("%Y-%m-%d %H:%M:%S")
    if i % 750 == 0:
        v = random.randint(50,60)
    data_logger.info("%s,%s" % (formatted_time, v))


'''
def dateparse (time_in_secs):
    return datetime.datetime.strptime(time_in_secs, '%Y-%m-%d %H:%M:%S')

all_filenames = glob.glob('./logs/sensor_1.log*')
all_filenames.sort()


all_filenames2 = glob.glob('./logs/sensor_2.log*')
all_filenames2.sort()

combined_csv = pd.concat([pd.read_csv(f, parse_dates=True, date_parser=dateparse, index_col='DateTime', names=['DateTime', 'Sensor1'], header=None) for f in all_filenames])
combined_csv2 = pd.concat([pd.read_csv(f, parse_dates=True, date_parser=dateparse, index_col='DateTime', names=['DateTime', 'Sensor2'], header=None) for f in all_filenames2])


print(combined_csv)
print(combined_csv2)


m2 = pd.merge(combined_csv, combined_csv2, how='inner', left_index=True, right_index=True)

print(m2)

m2.plot()

m2.plot(y=['Sensor1','Sensor2'])

ts = combined_csv.Sensor1.resample('5000s').max()

#ts.plot(y='Sensor1')

i = 0
def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()



data = {"time": ts.index.tolist(), "data": ts.tolist()}
s1 = json.dumps(data, default = myconverter)

plt.show()
