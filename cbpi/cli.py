import argparse
import logging

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

def create_config_file():
    import os.path
    if os.path.exists(os.path.join(".", 'config', "config.yaml")) is False:
        srcfile = os.path.join(os.path.dirname(__file__), "config", "config.yaml")
        destfile = os.path.join(".", 'config')
        shutil.copy(srcfile, destfile)

def create_home_folder_structure():
    pathlib.Path(os.path.join(".", 'logs/sensors')).mkdir(parents=True, exist_ok=True)
    pathlib.Path(os.path.join(".", 'config')).mkdir(parents=True, exist_ok=True)

def copy_splash():
    srcfile = os.path.join(os.path.dirname(__file__), "config", "splash.png")
    destfile = os.path.join(".", 'config')
    shutil.copy(srcfile, destfile)

def main():
    parser = argparse.ArgumentParser(description='Welcome to CraftBeerPi 4')
    parser.add_argument("action", type=str, help="start,stop,restart,setup")

    args = parser.parse_args()

    #logging.basicConfig(level=logging.INFO, filename='./logs/app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')

    if args.action == "setup":
        create_home_folder_structure()
        create_plugin_file()
        create_config_file()
        copy_splash()

    if args.action == "start":

        cbpi = CraftBeerPi()
        cbpi.start()

    parser.print_help()




