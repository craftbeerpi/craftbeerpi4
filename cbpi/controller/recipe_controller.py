import logging
from datetime import datetime
import os.path
from os import listdir
from os.path import isfile, join
import json
import shortuuid
import yaml
from ..api.step import StepMove, StepResult, StepState

import re

TIME_FORMAT = "%y-%m-%d.%H_%M"


class RecipeController:

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.logger = logging.getLogger(__name__)
        self.recipes_by_id = dict()

    def urlify(self, s):
        # Remove all non-word characters (everything except numbers and letters)
        s = re.sub(r"[^\w\s]", '', s)

        # Replace all runs of whitespace with a single dash
        s = re.sub(r"\s+", '-', s)

        return s

    def __get_filename(self, ind):
        name_by_id = self.recipes_by_id.get(ind)
        if name_by_id:
            return name_by_id
        return ind

    async def create(self, name):
        id = shortuuid.uuid()
        time = datetime.now().strftime(TIME_FORMAT)
        self.recipes_by_id[id] = name + '.' + time
        path = os.path.join(".", 'config', "recipes", "{}.yaml".format(self.recipes_by_id[id]))
        data = dict(basic=dict(name=name, author=self.cbpi.config.get("AUTHOR", "John Doe"), creation_time=time, id=id),
                    steps=[])
        with open(path, "w") as file:
            yaml.dump(data, file)
        return id

    async def save(self, name, data):
        self.recipes_by_id[name] = data["basic"]["name"] + '.' + data["basic"]["creation_time"]
        path = os.path.join(".", 'config', "recipes", "{}.yaml".format(self.recipes_by_id[name]))
        with open(path, "w") as file:
            yaml.dump(data, file, indent=4, sort_keys=True)
        
    async def get_recipes(self):
        path = os.path.join(".", 'config', "recipes")
        onlyfiles = [os.path.splitext(f)[0] for f in listdir(path) if isfile(join(path, f)) and f.endswith(".yaml")]

        result = []
        for filename in onlyfiles:
            recipe_path = os.path.join(".", 'config', "recipes", "{}.yaml".format(filename))
            with open(recipe_path) as file:
                data = yaml.load(file, Loader=yaml.FullLoader)
                dataset = data["basic"]
                self.recipes_by_id[dataset["id"]] = dataset["name"] + '.' + dataset["creation_time"]
                dataset["file"] = filename
                result.append(dataset)
        return result

    async def get_by_name(self, name):
        recipe_path = os.path.join(".", 'config', "recipes", "{}.yaml".format(self.__get_filename(name)))
        with open(recipe_path) as file:
            return yaml.load(file, Loader=yaml.FullLoader)

    async def remove(self, name):
        path = os.path.join(".", 'config', "recipes", "{}.yaml".format(self.__get_filename(name)))
        with open(path) as file:
            rec = yaml.load(file, Loader=yaml.FullLoader)
        rec_name, rec_id = rec["basic"]["name"], rec["basic"]["id"]
        os.remove(path)

    async def brew(self, name):
        recipe_path = os.path.join(".", 'config', "recipes", "{}.yaml".format(self.__get_filename(name)))
        with open(recipe_path) as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            await self.cbpi.step.load_recipe(data)

    async def clone(self, name, new_name):
        recipe_path = os.path.join(".", 'config', "recipes", "{}.yaml".format(self.__get_filename(name)))
        with open(recipe_path) as file:
            data = yaml.load(file, Loader=yaml.FullLoader)
            data["basic"]["name"] = new_name
            new_id = shortuuid.uuid()
            time = datetime.now().strftime(TIME_FORMAT)
            data["basic"]["id"] = new_id
            data["basic"]["creation_time"] = time
            await self.save(new_id, data)
            return new_id
