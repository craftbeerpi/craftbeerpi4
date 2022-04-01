
import logging
import os.path
from os import listdir
from os.path import isfile, join
import json
import shortuuid
import yaml
from ..api.step import StepMove, StepResult, StepState

import re

class FermenterRecipeController:


    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.logger = logging.getLogger(__name__)
    
    def urlify(self, s):

        # Remove all non-word characters (everything except numbers and letters)
        s = re.sub(r"[^\w\s]", '', s)

        # Replace all runs of whitespace with a single dash
        s = re.sub(r"\s+", '-', s)

        return s

    async def create(self, name):
        id = shortuuid.uuid()
        path = self.cbpi.config_folder.get_fermenter_recipe_by_id(id)
        data = dict(basic=dict(name=name), steps=[])
        with open(path, "w") as file:
            yaml.dump(data, file)
        return id

    async def save(self, name, data):
        path = self.cbpi.config_folder.get_fermenter_recipe_by_id(name)
        logging.info(data)
        with open(path, "w") as file:
            yaml.dump(data, file, indent=4, sort_keys=True)
        
        
    async def get_recipes(self):
        fermenter_recipes = self.cbpi.config_folder.get_all_fermenter_recipes()

        result = []
        for filename in fermenter_recipes:
            with open(filename) as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
                dataset = data["basic"]
                dataset["file"] = filename
                result.append(dataset)
                logging.info(result)
        return result

    async def get_by_name(self, name):
        recipe_path = self.cbpi.config_folder.get_fermenter_recipe_by_id(name)
        with open(recipe_path) as file:
            return  yaml.load(file, Loader=yaml.FullLoader)

    async def remove(self, name):
        path = self.cbpi.config_folder.get_fermenter_recipe_by_id(name)
        os.remove(path)

    async def brew(self, recipeid, fermenterid, name):
        recipe_path = self.cbpi.config_folder.get_fermenter_recipe_by_id(recipeid)

        logging.info(recipe_path)
        with open(recipe_path) as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            await self.cbpi.fermenter.load_recipe(data, fermenterid, name)

    async def clone(self, id, new_name):
        recipe_path = self.cbpi.config_folder.get_fermenter_recipe_by_id(id)
        with open(recipe_path) as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            data["basic"]["name"] = new_name
            new_id = shortuuid.uuid()
            await self.save(new_id, data)

            return new_id
