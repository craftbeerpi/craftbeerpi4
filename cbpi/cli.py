import logging
import requests
import yaml
from cbpi.configFolder import ConfigFolder
from cbpi.utils.utils import load_config
from zipfile import ZipFile
from cbpi.craftbeerpi import CraftBeerPi
import os
import pathlib
import pkgutil
import shutil
import yaml
import click
from subprocess import call
from colorama import Fore, Back, Style
import importlib
from importlib_metadata import metadata
from tabulate import tabulate
from PyInquirer import prompt, print_json

def create_home_folder_structure(configFolder):
    pathlib.Path(os.path.join(".", 'logs/sensors')).mkdir(parents=True, exist_ok=True)
    
    configFolder.create_folders()
    print("Folder created")


def setup_one_wire():
    print("Setting up 1Wire")
    with open('/boot/config.txt', 'w') as f:
        f.write("dtoverlay=w1-gpio,gpiopin=4,pullup=on")
    print("/boot/config.txt created")

def list_one_wire():
    print("List 1Wire")
    call(["modprobe", "w1-gpio"])
    call(["modprobe", "w1-therm"])
    try:
        for dirname in os.listdir('/sys/bus/w1/devices'):
            if (dirname.startswith("28") or dirname.startswith("10")):
                print(dirname)
    except Exception as e:
        print(e)


def plugins_list():
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


def plugin_create():
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

    name = "cbpi4_" + answers["name"]
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


@click.group()
@click.pass_context
@click.option('--config-folder-path', '-c', default="./config", type=click.Path(), help="Specify where the config folder is located. Defaults to './config'.")
def main(context, config_folder_path):
    print("---------------------")
    print("Welcome to CBPi")
    print("---------------------")
    level = logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    context.obj = ConfigFolder(config_folder_path)
    pass


@main.command()
@click.pass_context
def setup(context):
    '''Create Config folder'''
    print("Setting up CraftBeerPi")
    create_home_folder_structure(context.obj)
    context.obj.create_config_file()


@main.command()
@click.option('--list', is_flag=True, help="List all 1Wire Devices")
@click.option('--setup', is_flag=True, help="Setup 1Wire on Raspberry Pi")
def onewire(list, setup):
    '''Setup 1wire on Raspberry Pi'''
    if setup is True:
        setup_one_wire()
    if list is True:
        list_one_wire()


@main.command()
@click.pass_context
def start(context):
    '''Lets go brewing'''
    if context.obj.check_for_setup() is False:
        return
    print("Starting up CraftBeerPi ...")
    cbpi = CraftBeerPi(context.obj)
    cbpi.start()


@main.command()
@click.pass_context
def plugins(context):
    '''List active plugins'''
    plugins_list()
    return


@click.command()
def create():
    '''Create New Plugin'''
    plugin_create()


@main.command()
@click.argument('name')
@click.pass_context
def autostart(context, name):
    '''(on|off|status) Enable or disable autostart'''
    if(name == "status"):
        if os.path.exists(os.path.join("/etc/systemd/system","craftbeerpi.service")) is True:
            print("CraftBeerPi Autostart is {}ON{}".format(Fore.LIGHTGREEN_EX,Style.RESET_ALL))
        else:
            print("CraftBeerPi Autostart is {}OFF{}".format(Fore.RED,Style.RESET_ALL))
    elif(name == "on"):
        print("Add craftbeerpi.service to systemd")
        try:
            if os.path.exists(os.path.join("/etc/systemd/system","craftbeerpi.service")) is False:
                srcfile = context.obj.get_file_path("craftbeerpi.service")
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


@main.command()
@click.argument('name')
@click.pass_context
def chromium(context, name):
    '''(on|off|status) Enable or disable Kiosk mode'''
    if(name == "status"):
        if os.path.exists(os.path.join("/etc/xdg/autostart/","chromium.desktop")) is True:
            print("CraftBeerPi Chromium Desktop is {}ON{}".format(Fore.LIGHTGREEN_EX,Style.RESET_ALL))
        else:
            print("CraftBeerPi Chromium Desktop is {}OFF{}".format(Fore.RED,Style.RESET_ALL))
    elif(name == "on"):
        print("Add chromium.desktop to /etc/xdg/autostart/")
        try:
            if os.path.exists(os.path.join("/etc/xdg/autostart/","chromium.desktop")) is False:
                srcfile = context.obj.get_file_path("chromium.desktop")
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