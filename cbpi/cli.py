import argparse
import datetime
import logging
import subprocess
import sys
import re
import requests
import yaml
from cbpi.utils.utils import load_config
from zipfile import ZipFile
from cbpi.craftbeerpi import CraftBeerPi
import os
import pathlib
import shutil
import yaml
import click

from jinja2 import Template

def create_config_file():
    import os.path
    if os.path.exists(os.path.join(".", 'config', "config.yaml")) is False:
        srcfile = os.path.join(os.path.dirname(__file__), "config", "config.yaml")
        destfile = os.path.join(".", 'config')
        shutil.copy(srcfile, destfile)
        print("Config Folder created")

    if os.path.exists(os.path.join(".", 'config', "actor.json")) is False:
        srcfile = os.path.join(os.path.dirname(__file__), "config", "actor.json")
        destfile = os.path.join(".", 'config')
        shutil.copy(srcfile, destfile)

    if os.path.exists(os.path.join(".", 'config', "sensor.json")) is False:
        srcfile = os.path.join(os.path.dirname(__file__), "config", "sensor.json")
        destfile = os.path.join(".", 'config')
        shutil.copy(srcfile, destfile)

    if os.path.exists(os.path.join(".", 'config', "kettle.json")) is False:
        srcfile = os.path.join(os.path.dirname(__file__), "config", "kettle.json")
        destfile = os.path.join(".", 'config')
        shutil.copy(srcfile, destfile)

    if os.path.exists(os.path.join(".", 'config', "step_data.json")) is False:
        srcfile = os.path.join(os.path.dirname(__file__), "config", "step_data.json")
        destfile = os.path.join(".", 'config')
        shutil.copy(srcfile, destfile)

    if os.path.exists(os.path.join(".", 'config', "dashboard", "cbpi_dashboard_1.json")) is False:
        srcfile = os.path.join(os.path.dirname(__file__), "config", "dashboard", "cbpi_dashboard_1.json")
        destfile = os.path.join(".", "config", "dashboard")
        shutil.copy(srcfile, destfile)


def create_home_folder_structure():
    pathlib.Path(os.path.join(".", 'logs/sensors')).mkdir(parents=True, exist_ok=True)
    pathlib.Path(os.path.join(".", 'config')).mkdir(parents=True, exist_ok=True)
    pathlib.Path(os.path.join(".", 'config/dashboard')).mkdir(parents=True, exist_ok=True)
    pathlib.Path(os.path.join(".", 'config/dashboard/widgets')).mkdir(parents=True, exist_ok=True)
    print("Folder created")

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


def plugins_add(package_name):
    if package_name is None:
        print("Pleaes provide a plugin Name")
        return
    try:
        with open(os.path.join(".", 'config', "config.yaml"), 'rt') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            if package_name in data["plugins"]:
                print("")
                print("Plugin {} already active".format(package_name))
                print("")
                return
            data["plugins"].append(package_name)
        with open(os.path.join(".", 'config', "config.yaml"), 'w') as outfile:
            yaml.dump(data, outfile, default_flow_style=False)
        print("")
        print("Plugin {} activated".format(package_name))
        print("")
    except Exception as e:
        print(e)
        pass



def plugin_remove(package_name):
    if package_name is None:
        print("Pleaes provide a plugin Name")
        return
    try:
        with open(os.path.join(".", 'config', "config.yaml"), 'rt') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            
            data["plugins"] = list(filter(lambda k: package_name not in k, data["plugins"]))
            with open(os.path.join(".", 'config', "config.yaml"), 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)
        print("")        
        print("Plugin {} deactivated".format(package_name))
        print("")
    except Exception as e:
        print(e)
        pass

def plugins_list():

    print("--------------------------------------")
    print("List of active pluigins")
    try:
        with open(os.path.join(".", 'config', "config.yaml"), 'rt') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
            
            for p in data["plugins"]:
                print("- {}".format(p))
    except Exception as e:
        print(e)
        pass
    print("--------------------------------------")

def plugin_create(name):

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
    
    TEMPLATE_FILE = os.path.join("/", name , "config.yaml")
    template = templateEnv.get_template(TEMPLATE_FILE)
    outputText = template.render(name=name) 
    
    with open(os.path.join(".", name, name, "config.yaml"), "w") as fh:
        fh.write(outputText)
    print("")
    print("")
    print("Plugin {} created! See https://craftbeerpi.gitbook.io/craftbeerpi4/development how to run your plugin ".format(name))
    print("")
    print("Happy Development! Cheers")
    print("")
    print("")



@click.group()
def main():   
    level =logging.INFO
    logging.basicConfig(level=level, format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')  
    pass


@click.command()
def setup():
    '''Create Config folder'''
    print("Setting up CraftBeerPi")
    create_home_folder_structure()
    create_config_file()

@click.command()
def start():
    if check_for_setup() is False:
        return
    print("START")
    cbpi = CraftBeerPi()
    cbpi.start()

@click.command()
def plugins():
    '''List active plugins'''
    plugins_list()
    return

@click.command()
@click.argument('name')
def add(name):
    '''Activate Plugin'''
    plugins_add(name)

@click.command()
@click.argument('name')
def remove(name):
    '''Deactivate Plugin'''
    plugin_remove(name)
    

@click.command()
@click.argument('name')
def create(name):
    '''Deactivate Plugin'''
    plugin_create(name)

main.add_command(setup)
main.add_command(start)
main.add_command(plugins)
main.add_command(add)
main.add_command(remove)
main.add_command(create)
