import logging
import json
import os
from os import listdir
from os.path import isfile, join

class DashboardController:


    def __init__(self, cbpi):
        self.caching = False
        self.cbpi = cbpi
        self.logger = logging.getLogger(__name__)
        self.cbpi.register(self)

        self.path = os.path.join(".", 'config', "cbpi_dashboard_1.json")

    async def init(self):
        pass

    async def get_content(self, dashboard_id):
        try:
            with open(self.path) as json_file:
                data = json.load(json_file)
                return data
        except:
            return {}
    
    async def add_content(self, dashboard_id, data):
        with open(self.path, 'w') as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)
        return {"status": "OK"}

    async def delete_content(self, dashboard_id):
        if os.path.exists(self.path):
            os.remove(self.path)

    async def get_custom_widgets(self):
        path = os.path.join(".", 'config', "dashboard", "widgets")
        onlyfiles = [os.path.splitext(f)[0] for f in listdir(path) if isfile(join(path, f)) and f.endswith(".svg")]
        return onlyfiles
