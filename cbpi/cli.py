import argparse
import datetime
import logging
import subprocess
import sys
import re
import requests
import yaml
from cbpi.utils.utils import load_config

from cbpi.craftbeerpi import CraftBeerPi
import os
import pathlib
import shutil


def create_plugin_file():
    import os.path
    if os.path.exists(os.path.join(".", 'config', "plugin_list.txt")) is False:
        srcfile = os.path.join(os.path.dirname(__file__), "config", "plugin_list.txt")
        destfile = os.path.join(".", 'config')
        shutil.copy(srcfile, destfile)
        print("Plugin Folder created")

def create_config_file():
    import os.path
    if os.path.exists(os.path.join(".", 'config', "config.yaml")) is False:
        srcfile = os.path.join(os.path.dirname(__file__), "config", "config.yaml")
        destfile = os.path.join(".", 'config')
        shutil.copy(srcfile, destfile)
        print("Config Folder created")

def create_home_folder_structure():
    pathlib.Path(os.path.join(".", 'logs/sensors')).mkdir(parents=True, exist_ok=True)
    pathlib.Path(os.path.join(".", 'config')).mkdir(parents=True, exist_ok=True)
    print("Log Folder created")

def copy_splash():
    srcfile = os.path.join(os.path.dirname(__file__), "config", "splash.png")
    destfile = os.path.join(".", 'config')
    shutil.copy(srcfile, destfile)
    print("Splash Srceen created")

def clear_db():
    import os.path
    if os.path.exists(os.path.join(".", "craftbeerpi.db")) is True:
        os.remove(os.path.join(".", "craftbeerpi.db"))
        print("database Cleared")


def check_for_setup():

    if os.path.exists(os.path.join(".", "config", "config.yaml")) is False:
        print("***************************************************")
        print("CraftBeerPi Config File not found: %s" % os.path.join(".", "config", "config.yaml"))
        print("Please run 'cbpi setup' before starting the server ")
        print("***************************************************")
        return False
    else:
        return True


def list_plugins():
    print("***************************************************")
    print("CraftBeerPi 4.x Plugin List")
    print("***************************************************")
    print("")
    plugins_yaml = "https://raw.githubusercontent.com/Manuel83/craftbeerpi-plugins/master/plugins_v4.yaml"
    r = requests.get(plugins_yaml)
    data = yaml.load(r.content, Loader=yaml.FullLoader)
    for name, value in data.items():
        print(name)
    print("")
    print("***************************************************")

def add(package_name):

    if package_name is None:
        print("Missing Plugin Name: cbpi add --name=")
        return

    data = subprocess.check_output([sys.executable, "-m", "pip", "install", package_name])
    data = data.decode('UTF-8')

    patter_already_installed = "Requirement already satisfied: %s" % package_name
    pattern = "Successfully installed %s-([-0-9a-zA-Z._]*)" % package_name

    match_already_installed = re.search(patter_already_installed, data)
    match_installed = re.search(pattern, data)

    if match_already_installed is not None:
        print("Plugin already installed")
        return False

    if match_installed is None:
        print(data)
        print("Faild to install plugin")
        return False

    version = match_installed.groups()[0]
    plugins = load_config("./config/plugin_list.txt")
    if plugins is None:
        plugins = {}
    now = datetime.datetime.now()
    plugins[package_name] = dict(version=version, installation_date=now.strftime("%Y-%m-%d %H:%M:%S"))

    with open('./config/plugin_list.txt', 'w') as outfile:
        yaml.dump(plugins, outfile, default_flow_style=False)

    print("Plugin %s added" % package_name)
    return True


def remove(package_name):
    if package_name is None:
        print("Missing Plugin Name: cbpi add --name=")
        return
    data = subprocess.check_output([sys.executable, "-m", "pip", "uninstall", "-y", package_name])
    data = data.decode('UTF-8')

    pattern = "Successfully uninstalled %s-([-0-9a-zA-Z._]*)" % package_name
    match_uninstalled = re.search(pattern, data)

    if match_uninstalled is None:
        print(data)
        print("Faild to uninstall plugin")
        return False

    plugins = load_config("./config/plugin_list.txt")
    if plugins is None:
        plugins = {}

    if package_name not in plugins:
        return False

    del plugins[package_name]
    with open('./config/plugin_list.txt', 'w') as outfile:
        yaml.dump(plugins, outfile, default_flow_style=False)

    print("Plugin %s removed" % package_name)
    return True

def main():
    
    parser = argparse.ArgumentParser(description='Welcome to CraftBeerPi 4')
    parser.add_argument("action", type=str, help="start,stop,restart,setup,plugins")
    parser.add_argument("--name", type=str, help="Plugin name")
    args = parser.parse_args()
    #logging.basicConfig(level=logging.INFO, filename='./logs/app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    if args.action == "setup":
        print("Setting up CBPi")
        create_home_folder_structure()
        create_plugin_file()
        create_config_file()
        copy_splash()
        return

    if args.action == "cleardb":
        clear_db()
        return

    if args.action == "plugins":
        list_plugins()
        return


    if args.action == "add":

        add(args.name)
        return

    if args.action == "remove":
        remove(args.name)
        return

    if args.action == "start":
        if check_for_setup() is False:
            return

        cbpi = CraftBeerPi()
        cbpi.start()
        return

    parser.print_help()




