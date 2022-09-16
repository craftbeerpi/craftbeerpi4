import logging
from pathlib import Path
import requests
from cbpi.configFolder import ConfigFolder
from cbpi.utils.utils import load_config
from zipfile import ZipFile
from cbpi.craftbeerpi import CraftBeerPi
import os
import pkgutil
import shutil
import click
import pathlib
from subprocess import call
from colorama import Fore, Back, Style
import importlib
from importlib_metadata import metadata
from tabulate import tabulate
from PyInquirer import prompt, print_json
import platform

class CraftBeerPiCli():
    def __init__(self, config) -> None:
        self.config = config
        pass

    def setup(self):
        print("Setting up CraftBeerPi")
        self.config.create_home_folder_structure()
        self.config.create_config_file()

    def start(self):
        if self.config.check_for_setup() is False:
            return
        print("START")
        cbpi = CraftBeerPi(self.config)
        cbpi.start()

    def setup_one_wire(self):
        print("Setting up 1Wire")
        with open('/boot/config.txt', 'w') as f:
            f.write("dtoverlay=w1-gpio,gpiopin=4,pullup=on")
        print("/boot/config.txt created")

    def list_one_wire(self):
        print("List 1Wire")
        call(["modprobe", "w1-gpio"])
        call(["modprobe", "w1-therm"])
        try:
            for dirname in os.listdir('/sys/bus/w1/devices'):
                if (dirname.startswith("28") or dirname.startswith("10")):
                    print(dirname)
        except Exception as e:
            print(e)

    def plugins_list(self):
        result = []
        print("")
        print(Fore.LIGHTYELLOW_EX,"List of active plugins", Style.RESET_ALL)
        print("")
        discovered_plugins = {
            name: importlib.import_module(name)
            for finder, name, ispkg
            in pkgutil.iter_modules()
            if name.startswith('cbpi') and len(name) > 4
        }
        for key, module in discovered_plugins.items():
            try:
                meta = metadata(key)
                result.append(dict(Name=meta["Name"], Version=meta["Version"], Author=meta["Author"], Homepage=meta["Home-page"], Summary=meta["Summary"]))
                            
            except Exception as e:
                print(e)
        print(Fore.LIGHTGREEN_EX, tabulate(result, headers="keys"), Style.RESET_ALL)


    def plugin_create(self):
        print("Plugin Creation")
        print("")

        questions = [
            {
                'type': 'input',
                'name': 'name',
                'message': 'Plugin Name:',
            }
        ]

        answers = prompt(questions)

        name = "cbpi4-" + str(answers["name"]).replace('_', '-').replace(' ', '-')
        if os.path.exists(os.path.join(".", name)) is True:
            print("Cant create Plugin. Folder {} already exists ".format(name))
            return

        url = 'https://github.com/Manuel83/craftbeerpi4-plugin-template/archive/main.zip'
        r = requests.get(url)
        with open('temp.zip', 'wb') as f:
            f.write(r.content)

        with ZipFile('temp.zip', 'r') as repo_zip:
            repo_zip.extractall()

        os.rename("./craftbeerpi4-plugin-template-main", os.path.join(".", name))
        os.rename(os.path.join(".", name, "src"), os.path.join(".", name, name))

        import jinja2

        templateLoader = jinja2.FileSystemLoader(searchpath=os.path.join(".", name))
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = "setup.py"
        template = templateEnv.get_template(TEMPLATE_FILE)
        outputText = template.render(name=name)

        with open(os.path.join(".", name, "setup.py"), "w") as fh:
            fh.write(outputText)

        TEMPLATE_FILE = "MANIFEST.in"
        template = templateEnv.get_template(TEMPLATE_FILE)
        outputText = template.render(name=name)
        with open(os.path.join(".", name, "MANIFEST.in"), "w") as fh:
            fh.write(outputText)

        TEMPLATE_FILE = os.path.join("/", name, "config.yaml")
        operatingsystem = str(platform.system()).lower()
        if operatingsystem.startswith("win"):
            TEMPLATE_FILE=str(TEMPLATE_FILE).replace('\\','/')

        template = templateEnv.get_template(TEMPLATE_FILE)
        outputText = template.render(name=name)

        with open(os.path.join(".", name, name, "config.yaml"), "w") as fh:
            fh.write(outputText)

        print("")
        print("")
        print("Plugin {}{}{} created! ".format(Fore.LIGHTGREEN_EX, name, Style.RESET_ALL) )
        print("")
        print("Developer Documentation: https://openbrewing.gitbook.io/craftbeerpi4_support/readme/development")
        print("")
        print("Happy developing! Cheers")
        print("")
        print("")

    def autostart(self, name):
        '''Enable or disable autostart'''
        if(name == "status"):
            if os.path.exists(os.path.join("/etc/systemd/system","craftbeerpi.service")) is True:
                print("CraftBeerPi Autostart is {}ON{}".format(Fore.LIGHTGREEN_EX,Style.RESET_ALL))
            else:
                print("CraftBeerPi Autostart is {}OFF{}".format(Fore.RED,Style.RESET_ALL))
        elif(name == "on"):
            print("Add craftbeerpi.service to systemd")
            try:
                if os.path.exists(os.path.join("/etc/systemd/system","craftbeerpi.service")) is False:
                    srcfile = self.config.get_file_path("craftbeerpi.service")
                    destfile = os.path.join("/etc/systemd/system")
                    shutil.copy(srcfile, destfile)
                    print("Copied craftbeerpi.service to /etc/systemd/system")
                    os.system('systemctl enable craftbeerpi.service')
                    print('Enabled craftbeerpi service')
                    os.system('systemctl start craftbeerpi.service')
                    print('Started craftbeerpi.service')
                else:
                    print("craftbeerpi.service is already located in /etc/systemd/system")
            except Exception as e:
                print(e)
                return
            return
        elif(name == "off"): 
            print("Remove craftbeerpi.service from systemd")
            try:
                status = os.popen('systemctl list-units --type=service --state=running | grep craftbeerpi.service').read()
                if status.find("craftbeerpi.service") != -1:
                    os.system('systemctl stop craftbeerpi.service')
                    print('Stopped craftbeerpi service')
                    os.system('systemctl disable craftbeerpi.service')
                    print('Removed craftbeerpi.service as service')
                else:
                    print('craftbeerpi.service service is not running')

                if os.path.exists(os.path.join("/etc/systemd/system","craftbeerpi.service")) is True:
                    os.remove(os.path.join("/etc/systemd/system","craftbeerpi.service")) 
                    print("Deleted craftbeerpi.service from /etc/systemd/system")
                else:
                    print("craftbeerpi.service is not located in /etc/systemd/system")
            except Exception as e:
                print(e)
                return
            return


    def chromium(self, name):
        '''Enable or disable autostart'''
        if(name == "status"):
            if os.path.exists(os.path.join("/etc/xdg/autostart/","chromium.desktop")) is True:
                print("CraftBeerPi Chromium Desktop is {}ON{}".format(Fore.LIGHTGREEN_EX,Style.RESET_ALL))
            else:
                print("CraftBeerPi Chromium Desktop is {}OFF{}".format(Fore.RED,Style.RESET_ALL))
        elif(name == "on"):
            print("Add chromium.desktop to /etc/xdg/autostart/")
            try:
                if os.path.exists(os.path.join("/etc/xdg/autostart/","chromium.desktop")) is False:
                    srcfile = self.config.get_file_path("chromium.desktop")
                    destfile = os.path.join("/etc/xdg/autostart/")
                    shutil.copy(srcfile, destfile)
                    print("Copied chromium.desktop to /etc/xdg/autostart/")
                else:
                    print("chromium.desktop is already located in /etc/xdg/autostart/")
            except Exception as e:
                print(e)
                return
            return
        elif(name == "off"): 
            print("Remove chromium.desktop from /etc/xdg/autostart/")
            try:
                if os.path.exists(os.path.join("/etc/xdg/autostart/","chromium.desktop")) is True:
                    os.remove(os.path.join("/etc/xdg/autostart/","chromium.desktop"))
                    print("Deleted chromium.desktop from /etc/xdg/autostart/")
                else:
                    print("chromium.desktop is not located in /etc/xdg/autostart/")
            except Exception as e:
                print(e)
                return
            return


@click.group()
@click.pass_context
@click.option('--config-folder-path', '-c', default="./config", type=click.Path(), help="Specify where the config folder is located. Defaults to './config'.")
@click.option('--logs-folder-path', '-l', default="", type=click.Path(), help="Specify where the log folder is located. Defaults to '../logs' relative from the config folder.")
@click.option('--debug-log-level', '-d', default="30", type=int,  help="Specify the log level you want to write to all logs. 0=ALL, 10=DEBUG, 20=INFO 30(default)=WARNING, 40=ERROR, 50=CRITICAL")
def main(context, config_folder_path, logs_folder_path, debug_log_level):
    print("---------------------")
    print("Welcome to CBPi")
    print("---------------------")
    if logs_folder_path == "":
        logs_folder_path = os.path.join(Path(config_folder_path).absolute().parent, 'logs')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    logging.basicConfig(format=formatter,level=debug_log_level, stream=logging.StreamHandler())
    logger = logging.getLogger()
    try:
        if not os.path.isdir(logs_folder_path):
            logger.info(f"logs folder '{logs_folder_path}' doesnt exist and we are trying to create it")
            pathlib.Path(logs_folder_path).mkdir(parents=True, exist_ok=True)
            logger.info(f"logs folder '{logs_folder_path}' successfully created")
        logger.addHandler(logging.handlers.RotatingFileHandler(os.path.join(logs_folder_path, f"cbpi.log"), maxBytes=1000000, backupCount=3))
    except Exception as e:
        logger.warning("log folder or log file could not be created or accessed. check folder and file permissions or create the logs folder somewhere you have access with a start option like '--log-folder-path=./logs'")
        logging.critical(e, exc_info=True)
    cbpi_cli = CraftBeerPiCli(ConfigFolder(config_folder_path, logs_folder_path))
    context.obj = cbpi_cli

@main.command()
@click.pass_context
def setup(context):
    '''Create Config folder'''
    context.obj.setup()

@main.command()
@click.pass_context
@click.option('--list', is_flag=True, help="List all 1Wire Devices")
@click.option('--setup', is_flag=True, help="Setup 1Wire on Raspberry Pi")
def onewire(context, list, setup):
    '''Setup 1wire on Raspberry Pi'''
    if setup is True:
        context.obj.setup_one_wire()
    if list is True:
        context.obj.list_one_wire()

@main.command()
@click.pass_context
def start(context):
    context.obj.start()

@main.command()
@click.pass_context
def plugins(context):
    '''List active plugins'''
    context.obj.plugins_list()

@main.command()
@click.pass_context
def create(context):
    '''Create New Plugin'''
    context.obj.plugin_create()

@main.command()
@click.pass_context
@click.argument('name')
def autostart(context, name):
    '''(on|off|status) Enable or disable autostart'''
    context.obj.autostart(name)


@main.command()
@click.pass_context
@click.argument('name')
def chromium(context, name):
    '''(on|off|status) Enable or disable Kiosk mode'''
    context.obj.chromium(name)
