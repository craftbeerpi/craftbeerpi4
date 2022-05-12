import os
from os import listdir
from os.path import isfile, join
import pathlib
import platform
import shutil
import zipfile
import glob


class ConfigFolder:
    def __init__(self, configFolderPath):
        self._rawPath = configFolderPath

    def config_file_exists(self, path):
        return os.path.exists(self.get_file_path(path))
    
    def get_file_path(self, file):
        return os.path.join(self._rawPath, file)

    def get_upload_file(self, file):
        return os.path.join(self._rawPath, 'upload', file)

    def get_recipe_file_by_id(self, recipe_id):
        return os.path.join(self._rawPath, 'recipes', "{}.yaml".format(recipe_id))

    def get_fermenter_recipe_by_id(self, recipe_id):
        return os.path.join(self._rawPath, 'fermenterrecipes', "{}.yaml".format(recipe_id))

    def get_all_fermenter_recipes(self):
        fermenter_recipes_folder = os.path.join(self._rawPath, 'fermenterrecipes')
        fermenter_recipe_ids = [os.path.splitext(f)[0] for f in listdir(fermenter_recipes_folder) if isfile(join(fermenter_recipes_folder, f)) and f.endswith(".yaml")]
        return fermenter_recipe_ids

    def check_for_setup(self):
        if self.config_file_exists("config.yaml") is False:
            print("***************************************************")
            print("CraftBeerPi Config File not found: %s" % self.get_file_path("config.yaml"))
            print("Please run 'cbpi setup' before starting the server ")
            print("***************************************************")
            return False
        if self.config_file_exists("upload") is False:
            print("***************************************************")
            print("CraftBeerPi upload folder not found: %s" % self.get_file_path("upload"))
            print("Please run 'cbpi setup' before starting the server ")
            print("***************************************************")
            return False
    #    if os.path.exists(os.path.join(".", "config", "fermenterrecipes")) is False:
    #        print("***************************************************")
    #        print("CraftBeerPi fermenterrecipes folder not found: %s" % os.path.join(".", "config/fermenterrecipes"))
    #        print("Please run 'cbpi setup' before starting the server ")
    #        print("***************************************************")
    #        return False
        backupfile = os.path.join(".", "restored_config.zip")
        if os.path.exists(os.path.join(backupfile)) is True:
            print("***************************************************")
            print("Found backup of config. Starting restore")
            required_content=['dashboard/', 'recipes/', 'upload/', 'config.json', 'config.yaml']
            zip=zipfile.ZipFile(backupfile)
            zip_content_list = zip.namelist()
            zip_content = True
            print("Checking content of zip file")
            for content in required_content:
                try:
                    check = zip_content_list.index(content)
                except:
                    zip_content = False

            if zip_content == True:
                print("Found correct content. Starting Restore process")
                output_path = pathlib.Path(self._rawPath)
                system = platform.system()
                print(system)
                if system != "Windows":
                    owner = output_path.owner()
                    group = output_path.group()
                print("Removing old config folder")
                shutil.rmtree(output_path, ignore_errors=True) 
                print("Extracting zip file to config folder")
                zip.extractall(output_path)
                zip.close()
                if system != "Windows":
                    print(f"Changing owner and group of config folder recursively to {owner}:{group}")
                    self.recursive_chown(output_path, owner, group)
                print("Removing backup file")
                os.remove(backupfile)
            else:
                print("Wrong Content in zip file. No restore possible")
                print("Removing zip file")
                os.remove(backupfile)
            print("***************************************************")

    def copyDefaultFileIfNotExists(self, file):
        if self.config_file_exists(file) is False:
            srcfile = os.path.join(os.path.dirname(__file__), "config", file)
            destfile = os.path.join(self._rawPath, file)
            shutil.copy(srcfile, destfile)

    def create_config_file(self):
        self.copyDefaultFileIfNotExists("config.yaml")
        self.copyDefaultFileIfNotExists("actor.json")
        self.copyDefaultFileIfNotExists("sensor.json")
        self.copyDefaultFileIfNotExists("kettle.json")
        self.copyDefaultFileIfNotExists("fermenter_data.json")
        self.copyDefaultFileIfNotExists("step_data.json")
        self.copyDefaultFileIfNotExists("config.json")
        self.copyDefaultFileIfNotExists("craftbeerpi.service")
        self.copyDefaultFileIfNotExists("chromium.desktop")

        if os.path.exists(os.path.join(self._rawPath, "dashboard", "cbpi_dashboard_1.json")) is False:
            srcfile = os.path.join(os.path.dirname(__file__), "config", "dashboard", "cbpi_dashboard_1.json")
            destfile = os.path.join(self._rawPath, "dashboard")
            shutil.copy(srcfile, destfile)

        print("Config Folder created")

    def create_home_folder_structure(configFolder):
        pathlib.Path(os.path.join(".", 'logs/sensors')).mkdir(parents=True, exist_ok=True)
        
        configFolder.create_folders()
        print("Folder created")

    def create_folders(self):
        pathlib.Path(self._rawPath).mkdir(parents=True, exist_ok=True)
        pathlib.Path(os.path.join(self._rawPath, 'dashboard', 'widgets')).mkdir(parents=True, exist_ok=True)
        pathlib.Path(os.path.join(self._rawPath, 'recipes')).mkdir(parents=True, exist_ok=True)
        pathlib.Path(os.path.join(self._rawPath, 'upload')).mkdir(parents=True, exist_ok=True)

    def recursive_chown(self, path, owner, group):
        for dirpath, dirnames, filenames in os.walk(path):
            shutil.chown(dirpath, owner, group)
            for filename in filenames:
                shutil.chown(os.path.join(dirpath, filename), owner, group)