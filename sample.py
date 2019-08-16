import datetime

import yaml
from cbpi.utils.utils import load_config

package_name = "test222"

with open("./config/plugin_list.txt", 'rt') as f:
    print(f)
    plugins = yaml.load(f)
    if plugins is None:
        plugins = {}


now = datetime.datetime.now()

plugins[package_name] = dict(version="1.0", installation_date=now.strftime("%Y-%m-%d %H:%M:%S"))
with open('./config/plugin_list.txt', 'w') as outfile:
    yaml.dump(plugins, outfile, default_flow_style=False)
