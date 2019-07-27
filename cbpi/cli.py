import argparse
import logging
import requests
import yaml

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
    plugins_yaml = "https://raw.githubusercontent.com/Manuel83/craftbeerpi-plugins/master/plugins_v4.yaml"
    r = requests.get(plugins_yaml)

    data = yaml.load(r.content, Loader=yaml.FullLoader)


    for name, value in data.items():
        print(name)


def main():
    parser = argparse.ArgumentParser(description='Welcome to CraftBeerPi 4')
    parser.add_argument("action", type=str, help="start,stop,restart,setup,plugins")

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

    if args.action == "plugins":
        list_plugins()
        return

    if args.action == "start":
        if check_for_setup() is False:
            return

        cbpi = CraftBeerPi()
        cbpi.start()
        return

    parser.print_help()




