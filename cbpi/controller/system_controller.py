import logging
import os
import shutil
import psutil
import pathlib
import aiohttp
from voluptuous.schema_builder import message
from cbpi.api.dataclasses import NotificationAction, NotificationType
from cbpi.api.base import CBPiBase
from cbpi.api.config import ConfigType
from cbpi.api import *
import zipfile
import socket

class SystemController:

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.service = cbpi.actor
        self.logger = logging.getLogger(__name__)

        self.cbpi.app.on_startup.append(self.check_for_update)


    async def check_for_update(self, app):
        pass

    async def restart(self):
        logging.info("RESTART")
        os.system('systemctl reboot') 
        pass

    async def shutdown(self):
        logging.info("SHUTDOWN")
        os.system('systemctl poweroff') 
        pass

    async def backupConfig(self):
        output_filename = "cbpi4_config"
        dir_name = pathlib.Path(os.path.join(".", 'config'))
        shutil.make_archive(output_filename, 'zip', dir_name)

    def allowed_file(self, filename, extension):
        return '.' in filename and filename.rsplit('.', 1)[1] in set([extension])

    def recursive_chown(self, path, owner, group):
        for dirpath, dirnames, filenames in os.walk(path):
            shutil.chown(dirpath, owner, group)
            for filename in filenames:
                shutil.chown(os.path.join(dirpath, filename), owner, group)

    async def restoreConfig(self, data):
        fileData = data['File']
        filename = fileData.filename
        backup_file = fileData.file
        content_type = fileData.content_type
        required_content=['dashboard/', 'recipes/', 'upload/', 'config.json', 'config.yaml']

        if content_type == 'application/x-zip-compressed':
            try:
                content = backup_file.read()
                if backup_file and self.allowed_file(filename, 'zip'):
                    self.path = os.path.join(".", "restored_config.zip")

                    f=open(self.path, "wb")
                    f.write(content)
                    f.close()
                    zip=zipfile.ZipFile(self.path)
                    zip_content_list = zip.namelist()
                    zip_content = True
                    for content in required_content:
                        try:
                            check = zip_content_list.index(content)
                        except:
                            zip_content = False
                    if zip_content == True:
                        self.cbpi.notify("Success", "Config backup has been uploaded", NotificationType.SUCCESS)
                        self.cbpi.notify("Action Required!", "Please restart the server", NotificationType.WARNING)
                    else:
                        self.cbpi.notify("Error", "Wrong content type. Upload failed", NotificationType.ERROR)
                        os.remove(self.path)
            except:
                self.cbpi.notify("Error", "Config backup upload failed", NotificationType.ERROR)
                pass
        else:
            self.cbpi.notify("Error", "Wrong content type. Upload failed", NotificationType.ERROR)

    async def systeminfo(self):
        logging.info("SYSTEMINFO")
        system = "" 
        temp = 0
        cpuload = 0
        cpucount = 0
        cpufreq = 0
        totalmem = 0
        availmem = 0
        mempercent = 0
        eth0IP = "N/A"
        wlan0IP = "N/A"

        TEMP_UNIT=self.cbpi.config.get("TEMP_UNIT", "C")
        FAHRENHEIT = False if TEMP_UNIT == "C" else True

        af_map = { socket.AF_INET: 'IPv4',
                   socket.AF_INET6: 'IPv6',
                   }

        try:
            if psutil.LINUX == True:
                system = "Linux"
            elif psutil.WINDOWS == True:
                system = "Windows"
            elif psutil.MACOS == True:
                system = "MacOS"
            cpuload = round(psutil.cpu_percent(interval=None),1)
            cpucount = psutil.cpu_count(logical=False)
            cpufreq = psutil.cpu_freq()
            mem = psutil.virtual_memory()
            availmem = round((int(mem.available) / (1024*1024)),1)
            mempercent = round(float(mem.percent),1)
            totalmem = round((int(mem.total) / (1024*1024)),1)
            if system == "Linux":
                try:
                    temps = psutil.sensors_temperatures(fahrenheit=FAHRENHEIT)
                    for name, entries in temps.items():
                        for entry in entries:
                            if name == "cpu_thermal":
                                temp = round(float(entry.current),1)
                except:
                    pass
            else:
                temp = "N/A"
            if system == "Linux":
                try:
                    ethernet = psutil.net_if_addrs()
                    for nic, addrs in ethernet.items():
                        if nic == "eth0":
                            for addr in addrs:
                                if str(addr.family) == "AddressFamily.AF_INET": 
                                    if addr.address:
                                        eth0IP = addr.address
                        if nic == "wlan0":
                            for addr in addrs:
                                if str(addr.family) == "AddressFamily.AF_INET": 
                                    if addr.address:
                                        wlan0IP = addr.address
                except:
                    pass

        except:
            pass

        systeminfo =    {'system': system,
                         'cpuload': cpuload,
                         'cpucount': cpucount,
                         'cpufreq': cpufreq.current,
                         'totalmem': totalmem,
                         'availmem': availmem,
                         'mempercent': mempercent,
                         'temp': temp,
                         'temp_unit': TEMP_UNIT,
                         'eth0': eth0IP,
                         'wlan0': wlan0IP}
        return systeminfo


