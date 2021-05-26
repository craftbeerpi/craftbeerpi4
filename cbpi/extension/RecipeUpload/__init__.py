
# -*- coding: utf-8 -*-
import os
import pathlib
import aiohttp
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
from cbpi.api import *
import xml.etree.ElementTree
import sqlite3
from voluptuous.schema_builder import message
from cbpi.api.dataclasses import NotificationAction, NotificationType
from cbpi.controller.kettle_controller import KettleController
from cbpi.api.base import CBPiBase
from cbpi.api.config import ConfigType
import json
import webbrowser

logger = logging.getLogger(__name__)

async def get_kbh_recipes():
    try:
        path = os.path.join(".", 'config', "upload", "kbh.db")
        conn = sqlite3.connect(path)
        c = conn.cursor()
        c.execute('SELECT ID, Sudname, Status FROM Sud')
        data = c.fetchall()
        result = []
        for row in data:
            element = {'value': str(row[0]), 'label': str(row[1])}
            result.append(element)
        return result
    except:
        return []

async def get_xml_recipes():
    try:
        path = os.path.join(".", 'config', "upload", "beer.xml")
        e = xml.etree.ElementTree.parse(path).getroot()
        result =[] 
        counter = 1
        for idx, val in enumerate(e.findall('RECIPE')):
            element = {'value': str(counter), 'label': val.find("NAME").text}
            result.append(element)
            counter +=1
        return result
    except:
        return []

class RecipeUpload(CBPiExtension):
    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.cbpi.register(self, "/upload")

    def allowed_file(self, filename, extension):
        return '.' in filename and filename.rsplit('.', 1)[1] in set([extension])

    @request_mapping(path='/', method="POST", auth_required=False)
    async def RecipeUpload(self, request):
        data = await request.post()
        fileData = data['File']
        logging.info(fileData)

        if fileData.content_type == 'text/xml':
            logging.info(fileData.content_type)
            try:
                filename = fileData.filename
                beerxml_file = fileData.file
                content = beerxml_file.read().decode()
                if beerxml_file and self.allowed_file(filename, 'xml'):
                    self.path = os.path.join(".", 'config', "upload", "beer.xml")
    
                    f = open(self.path, "w")
                    f.write(content)
                    f.close()
                self.cbpi.notify("Success", "XML Recipe {} has been uploaded".format(filename), NotificationType.SUCCESS)
            except:
                self.cbpi.notify("Error" "XML Recipe upload failed", NotificationType.ERROR)
                pass

        elif fileData.content_type == 'application/octet-stream':
            try:
                filename = fileData.filename
                logger.info(filename)
                kbh_file = fileData.file
                content = kbh_file.read()
                if kbh_file and self.allowed_file(filename, 'sqlite'):
                    self.path = os.path.join(".", 'config', "upload", "kbh.db")

                    f=open(self.path, "wb")
                    f.write(content)
                    f.close()
                self.cbpi.notify("Success", "Kleiner Brauhelfer database has been uploaded", NotificationType.SUCCESS)
            except:
                self.cbpi.notify("Error", "Kleiner Brauhelfer database upload failed", NotificationType.ERROR)
                pass
        else:
            self.cbpi.notify("Error", "Wrong content type. Upload failed", NotificationType.ERROR)

        return web.Response(status=200)

    @request_mapping(path='/kbh', method="GET", auth_required=False)
    async def get_kbh_list(self, request):
        kbh_list = await get_kbh_recipes()
        return web.json_response(kbh_list)

    @request_mapping(path='/kbh', method="POST", auth_required=False)
    async def create_kbh_recipe(self, request):
        kbh_id = await request.json()
        await self.kbh_recipe_creation(kbh_id['id'])
        return web.Response(status=200)

    @request_mapping(path='/xml', method="GET", auth_required=False)
    async def get_xml_list(self, request):
        xml_list = await get_xml_recipes()
        return web.json_response(xml_list)

    @request_mapping(path='/xml', method="POST", auth_required=False)
    async def create_xml_recipe(self, request):
        xml_id = await request.json()
        await self.xml_recipe_creation(xml_id['id'])
        return web.Response(status=200)

    async def kbh_recipe_creation(self, Recipe_ID):
        self.kettle = None

        #Define MashSteps
        self.mashin =  self.cbpi.config.get("steps_mashin", "MashInStep")
        self.mash = self.cbpi.config.get("steps_mash", "MashStep") 
        self.mashout = self.cbpi.config.get("steps_mashout", None) # Currently used only for the Braumeister 
        self.boil = self.cbpi.config.get("steps_boil", "BoilStep") 
        self.whirlpool="Waitstep"
        self.cooldown = self.cbpi.config.get("steps_cooldown", "WaitStep") 
        
        #get default boil temp from settings
        self.BoilTemp = self.cbpi.config.get("steps_boil_temp", 98)

        #get default cooldown temp alarm setting
        self.CoolDownTemp = self.cbpi.config.get("steps_cooldown_temp", 25)

        #get server port from settings and define url for api calls -> adding steps
        self.port = str(self.cbpi.static_config.get('port',8000))
        self.url="http://127.0.0.1:" + self.port + "/step2/"


        # get default Kettle from Settings       
        self.id = self.cbpi.config.get('MASH_TUN', None)
        try:
            self.kettle = self.cbpi.kettle.find_by_id(self.id) 
        except:
            self.cbpi.notify('Recipe Upload', 'No default Kettle defined. Please specify default Kettle in settings', NotificationType.ERROR)
        if self.id is not None or self.id != '':
            # load beerxml file located in upload folder
            self.path = os.path.join(".", 'config', "upload", "kbh.db")
            if os.path.exists(self.path) is False:
                self.cbpi.notify("File Not Found", "Please upload a kbh V2 databsel file", NotificationType.ERROR)
                
            try:
                conn = sqlite3.connect(self.path)
                c = conn.cursor()
                c.execute('SELECT Sudname FROM Sud WHERE ID = ?', (Recipe_ID,))
                row = c.fetchone()
                name = row[0]

                # Create recipe in recipe Book with name of first recipe in xml file
                self.recipeID = await self.cbpi.recipe.create(name)

                # send recipe to mash profile
                await self.cbpi.recipe.brew(self.recipeID)
    
                # remove empty recipe from recipe book
                await self.cbpi.recipe.remove(self.recipeID)

                #MashIn Step
                c.execute('SELECT Temp FROM Rasten WHERE Typ = 0 AND SudID = ?', (Recipe_ID,))
                row = c.fetchone()

                step_kettle = self.id
                step_name = "MashIn"
                step_timer = "0"
                step_temp = str(int(row[0]))
                sensor = self.kettle.sensor
                step_type = self.mashin if self.mashin != "" else "MashInStep"
                AutoMode = "Yes" if step_type == "MashInStep" else "No"
                Notification = "Target temperature reached. Please add malt."
                await self.create_step(step_type, step_name, step_kettle, step_timer, step_temp, AutoMode, sensor, Notification)

                for row in c.execute('SELECT Name, Temp, Dauer FROM Rasten WHERE Typ <> 0 AND SudID = ?', (Recipe_ID,)):
                    step_name = str(row[0])
                    step_temp = str(int(row[1]))
                    step_timer = str(int(row[2]))
                    step_type = self.mash if self.mash != "" else "MashStep"
                    AutoMode = "Yes" if step_type == "MashStep" else "No"
                    await self.create_step(step_type, step_name, step_kettle, step_timer, step_temp, AutoMode, sensor)

                # MashOut -> Notification step that sends notification and waits for user input to move to next step (AutoNext=No)
                if self.mashout == "NotificationStep":
                    step_kettle = self.id
                    step_type = self.mashout
                    step_name = "Lautering"
                    step_timer = ""
                    step_temp = ""
                    AutoMode = ""
                    sensor = ""
                    Notification = "Mash Process completed. Please start lautering and press next to start boil."
                    AutoNext = "No"
                    await self.create_step(step_type, step_name, step_kettle, step_timer, step_temp, AutoMode, sensor, Notification, AutoNext)

                c.execute('SELECT Kochdauer FROM Sud WHERE ID = ?', (Recipe_ID,))
                row = c.fetchone()
                step_time = str(int(row[0]))

                FirstWortFlag = self.getFirstWortKBH(Recipe_ID)

                BoilTimeAlerts = self.getBoilAlertsKBH(Recipe_ID)

                step_kettle = self.id
                step_type = self.boil if self.boil != "" else "BoilStep"
                step_name = "Boil Step"
                step_temp = int(self.BoilTemp)
                AutoMode = "Yes" if step_type == "BoilStep" else "No"
                sensor = self.kettle.sensor
                Notification = ""
                AutoNext = ""
                LidAlert = "Yes"
                FirstWort = 'Yes' if FirstWortFlag == True else 'No'
                Hop1 = str(int(BoilTimeAlerts[0])) if len(BoilTimeAlerts) >= 1 else None
                Hop2 = str(int(BoilTimeAlerts[1])) if len(BoilTimeAlerts) >= 2 else None
                Hop3 = str(int(BoilTimeAlerts[2])) if len(BoilTimeAlerts) >= 3 else None       
                Hop4 = str(int(BoilTimeAlerts[3])) if len(BoilTimeAlerts) >= 4 else None
                Hop5 = str(int(BoilTimeAlerts[4])) if len(BoilTimeAlerts) >= 5 else None
                Hop6 = str(int(BoilTimeAlerts[5])) if len(BoilTimeAlerts) >= 6 else None

                await self.create_step(step_type, step_name, step_kettle, step_time, step_temp, AutoMode, sensor, Notification, AutoNext, LidAlert, FirstWort, Hop1, Hop2, Hop3, Hop4, Hop5, Hop6)
 
                # Add Waitstep as Whirlpool
                if self.cooldown != "WaiStep" and self.cooldown !="":
                    step_type = "WaitStep"
                    step_name = "Whirlpool"
                    cooldown_sensor = ""
                    step_timer = "15"
                    step_temp = ""
                    AutoMode = ""

                    await self.create_step(step_type, step_name, step_kettle, step_timer, step_temp, AutoMode, cooldown_sensor)

                # CoolDown step is sending a notification when cooldowntemp is reached
                step_type = self.cooldown if self.cooldown != "" else "WaitStep"
                step_name = "CoolDown"
                cooldown_sensor = ""
                step_timer = "15"
                step_temp = ""
                AutoMode = ""
                if step_type == "CooldownStep":
                    cooldown_sensor = self.cbpi.config.get("steps_cooldown_sensor", None)
                    if cooldown_sensor is None or cooldown_sensor == '':
                        cooldown_sensor = self.kettle.sensor  # fall back to kettle sensor if no other sensor is specified
                    step_kettle = self.id
                    step_timer = ""                
                    step_temp = int(self.CoolDownTemp)
            
                await self.create_step(step_type, step_name, step_kettle, step_timer, step_temp, AutoMode, cooldown_sensor)

            except:
                pass

            self.cbpi.notify('KBH Recipe created', name, NotificationType.INFO)

    def getFirstWortKBH(self, id):
        alert = False
        try:
            conn = sqlite3.connect(self.path)
            c = conn.cursor()
            c.execute('SELECT Zeit FROM Hopfengaben WHERE Vorderwuerze = 1 AND SudID = ?', (id,))
            row = c.fetchall()
            if len(row) != 0:
                alert = True
        except Exception as e:
            self.cbpi.notify("Failed to create Recipe", e.message, NotificationType.ERROR)
            return ('', 500)
        finally:
            if conn:
                conn.close()

        return alert


    def getBoilAlertsKBH(self, id):
        alerts = []
        try:
            conn = sqlite3.connect(self.path)
            c = conn.cursor()
            # get the hop addition times
            c.execute('SELECT Zeit FROM Hopfengaben WHERE Vorderwuerze = 0 AND SudID = ?', (id,))
            rows = c.fetchall()
            
            for row in rows:
                alerts.append(float(row[0]))
                
            # get any misc additions if available
            c.execute('SELECT Zugabedauer FROM WeitereZutatenGaben WHERE Zeitpunkt = 1 AND SudID = ?', (id,))
            rows = c.fetchall()
            
            for row in rows:
                alerts.append(float(row[0]))
                
            ## Dedupe and order the additions by their time, to prevent multiple alerts at the same time
            alerts = sorted(list(set(alerts)))
            
            ## CBP should have these additions in reverse
            alerts.reverse()
        
        except Exception as e:
            self.cbpi.notify("Failed to create Recipe", e.message, NotificationType.ERROR)
            return ('', 500)
        finally:
            if conn:
                conn.close()
                
        return alerts

    async def xml_recipe_creation(self, Recipe_ID):
        self.kettle = None

        #Define MashSteps
        self.mashin =  self.cbpi.config.get("steps_mashin", "MashStep")
        self.mash = self.cbpi.config.get("steps_mash", "MashStep")
        self.mashout = self.cbpi.config.get("steps_mashout", None) # Currently used only for the Braumeister
        self.boil = self.cbpi.config.get("steps_boil", "BoilStep")
        self.cooldown = self.cbpi.config.get("steps_cooldown", "WaitStep")

        #get default boil temp from settings
        self.BoilTemp = self.cbpi.config.get("steps_boil_temp", 98)

        #get default cooldown temp alarm setting
        self.CoolDownTemp = self.cbpi.config.get("steps_cooldown_temp", 25)

        #get server port from settings and define url for api calls -> adding steps
        self.port = str(self.cbpi.static_config.get('port',8000))
        self.url="http://127.0.0.1:" + self.port + "/step2/"


        # get default Kettle from Settings
        self.id = self.cbpi.config.get('MASH_TUN', None)
        try:
            self.kettle = self.cbpi.kettle.find_by_id(self.id)
        except:
            self.cbpi.notify('Recipe Upload', 'No default Kettle defined. Please specify default Kettle in settings', NotificationType.ERROR)
        if self.id is not None or self.id != '':
            # load beerxml file located in upload folder
            self.path = os.path.join(".", 'config', "upload", "beer.xml")
            if os.path.exists(self.path) is False:
                self.cbpi.notify("File Not Found", "Please upload a Beer.xml File", NotificationType.ERROR)

            e = xml.etree.ElementTree.parse(self.path).getroot()

            result = []
            for idx, val in enumerate(e.findall('RECIPE')):
                result.append(val.find("NAME").text)

            # Create recipe in recipe Book with name of first recipe in xml file
            self.recipeID = await self.cbpi.recipe.create(self.getRecipeName(Recipe_ID))

            # send recipe to mash profile
            await self.cbpi.recipe.brew(self.recipeID)

            # remove empty recipe from recipe book
            await self.cbpi.recipe.remove(self.recipeID)

            # Mash Steps -> first step is different as it heats up to defined temp and stops with notification to add malt
            # AutoMode is yes to start and stop automatic mode or each step
            MashIn_Flag = True
            step_kettle = self.id
            for row in self.getSteps(Recipe_ID):
                step_name = str(row.get("name"))
                step_timer = str(int(row.get("timer")))
                step_temp = str(int(row.get("temp")))
                sensor = self.kettle.sensor
                if MashIn_Flag == True and row.get("timer") == 0:
                    step_type = self.mashin if self.mashin != "" else "MashInStep"
                    AutoMode = "Yes" if step_type == "MashInStep" else "No"
                    Notification = "Target temperature reached. Please add malt."
                    MashIn_Flag = False
                else:
                    step_type = self.mash if self.mash != "" else "MashStep"
                    AutoMode = "Yes" if step_type == "MashStep" else "No"
                    Notification = ""

                await self.create_step(step_type, step_name, step_kettle, step_timer, step_temp, AutoMode, sensor, Notification)

            # MashOut -> Simple step that sends notification and waits for user input to move to next step (AutoNext=No)
            if self.mashout == "NotificationStep":
                step_kettle = self.id
                step_type = self.mashout
                step_name = "Lautering"
                step_timer = ""
                step_temp = ""
                AutoMode = ""
                sensor = ""
                Notification = "Mash Process completed. Please start lautering and press next to start boil."
                AutoNext = "No"
                await self.create_step(step_type, step_name, step_kettle, step_timer, step_temp, AutoMode, sensor, Notification, AutoNext)

            # Boil step including hop alarms and alarm for first wort hops -> Automode is set tu yes
            FirstWortFlag = len(str(self.getFirstWortAlert(Recipe_ID)))
            self.BoilTimeAlerts = self.getBoilAlerts(Recipe_ID)

            step_kettle = self.id
            step_time = str(int(self.getBoilTime(Recipe_ID)))
            step_type = self.boil if self.boil != "" else "BoilStep"
            step_name = "Boil Step"
            step_temp = self.BoilTemp
            AutoMode = "Yes" if step_type == "BoilStep" else "No"
            sensor = self.kettle.sensor
            Notification = ""
            AutoNext = ""
            LidAlert = "Yes"
            FirstWort = 'Yes' if FirstWortFlag != 0 else 'No'
            Hop1 = str(int(self.BoilTimeAlerts[0])) if len(self.BoilTimeAlerts) >= 1 else None
            Hop2 = str(int(self.BoilTimeAlerts[1])) if len(self.BoilTimeAlerts) >= 2 else None
            Hop3 = str(int(self.BoilTimeAlerts[2])) if len(self.BoilTimeAlerts) >= 3 else None       
            Hop4 = str(int(self.BoilTimeAlerts[3])) if len(self.BoilTimeAlerts) >= 4 else None
            Hop5 = str(int(self.BoilTimeAlerts[4])) if len(self.BoilTimeAlerts) >= 5 else None 
            Hop6 = str(int(self.BoilTimeAlerts[5])) if len(self.BoilTimeAlerts) >= 6 else None


            await self.create_step(step_type, step_name, step_kettle, step_time, step_temp, AutoMode, sensor, Notification, AutoNext, LidAlert, FirstWort, Hop1, Hop2, Hop3, Hop4, Hop5, Hop6)

            # Add Waitstep as Whirlpool
            if self.cooldown != "WaiStep" and self.cooldown !="":
                step_type = "WaitStep"
                step_name = "Whirlpool"
                cooldown_sensor = ""
                step_timer = "15"
                step_temp = ""
                AutoMode = ""

                await self.create_step(step_type, step_name, step_kettle, step_timer, step_temp, AutoMode, cooldown_sensor)

            # CoolDown step is sending a notification when cooldowntemp is reached
            step_type = self.cooldown if self.cooldown != "" else "WaitStep"
            step_name = "CoolDown"
            cooldown_sensor = ""
            step_timer = "15"
            step_temp = ""
            AutoMode = ""
            if step_type == "CooldownStep":
                cooldown_sensor = self.cbpi.config.get("steps_cooldown_sensor", None)
                if cooldown_sensor is None or cooldown_sensor == '':
                    cooldown_sensor = self.kettle.sensor  # fall back to kettle sensor if no other sensor is specified
                step_kettle = self.id
                step_timer = ""                
                step_temp = self.CoolDownTemp
            
            await self.create_step(step_type, step_name, step_kettle, step_timer, step_temp, AutoMode, cooldown_sensor)

            self.cbpi.notify('BeerXML Recipe created ', result, NotificationType.INFO)

    # XML functions to retrieve xml repice parameters (if multiple recipes are stored in one xml file, id could be used)

    def getRecipeName(self, id):
        e = xml.etree.ElementTree.parse(self.path).getroot()
        return e.find('./RECIPE[%s]/NAME' % (str(id))).text

    def getBoilTime(self, id):
        e = xml.etree.ElementTree.parse(self.path).getroot()
        return float(e.find('./RECIPE[%s]/BOIL_TIME' % (str(id))).text)

    def getBoilAlerts(self, id):
        e = xml.etree.ElementTree.parse(self.path).getroot()
        
        recipe = e.find('./RECIPE[%s]' % (str(id)))
        alerts = []
        for e in recipe.findall('./HOPS/HOP'):
            use = e.find('USE').text
            ## Hops which are not used in the boil step should not cause alerts
            if use != 'Aroma' and use != 'Boil':
                continue
            
            alerts.append(float(e.find('TIME').text))
            ## There might also be miscelaneous additions during boild time
        for e in recipe.findall('MISCS/MISC[USE="Boil"]'):
            alerts.append(float(e.find('TIME').text))
            
        ## Dedupe and order the additions by their time, to prevent multiple alerts at the same time
        alerts = sorted(list(set(alerts)))
        ## CBP should have these additions in reverse
        alerts.reverse()
        
        return alerts

    def getFirstWortAlert(self, id):
        e = xml.etree.ElementTree.parse(self.path).getroot()
        recipe = e.find('./RECIPE[%s]' % (str(id)))
        alerts = []
        for e in recipe.findall('./HOPS/HOP'):
            use = e.find('USE').text
            ## Hops which are not used in the boil step should not cause alerts
            if use != 'First Wort':
                continue
            
            alerts.append(float(e.find('TIME').text))
            
        ## Dedupe and order the additions by their time, to prevent multiple alerts at the same time
        alerts = sorted(list(set(alerts)))
        ## CBP should have these additions in reverse
        alerts.reverse()
        
        return alerts

    def getSteps(self, id):
        e = xml.etree.ElementTree.parse(self.path).getroot()
        steps = []
        for e in e.findall('./RECIPE[%s]/MASH/MASH_STEPS/MASH_STEP' % (str(id))):
            if self.cbpi.config.get("TEMP_UNIT", "C") == "C":
                temp = float(e.find("STEP_TEMP").text)
            else:
                temp = round(9.0 / 5.0 * float(e.find("STEP_TEMP").text) + 32, 2)
            steps.append({"name": e.find("NAME").text, "temp": temp, "timer": float(e.find("STEP_TIME").text)})
            
        return steps

    # function to create json to be send to api to add a step to the current mash profile. Currently all properties are send to each step which does not cuase an issue
    async def create_step(self, type, name, kettle, timer, temp, AutoMode, sensor, Notification = "", AutoNext = "", LidAlert = "", FirstWort = "", Hop1 = "", Hop2 = "", Hop3 = "", Hop4 = "", Hop5 = "", Hop6=""):
        step_string = { "name": name,
                            "props": {
                                "AutoMode": AutoMode,
                                "Kettle": kettle,
                                "Sensor": sensor,
                                "Temp": temp,
                                "Timer": timer,
                                "Notification": Notification,
                                "AutoNext": AutoNext,
                                "First_Wort": FirstWort,
                                "LidAlert": LidAlert,
                                "Hop_1": Hop1,
                                "Hop_2": Hop2,
                                "Hop_3": Hop3,
                                "Hop_4": Hop4,
                                "Hop_5": Hop5,
                                "Hop_6": Hop6
                                },
                            "status_text": "",
                            "status": "I",
                            "type": type
                        }
        # convert step:string to json required for api call. 
        step = json.dumps(step_string)
        headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(self.url, data=step) as response:
                return await response.text()
                await self.push_update()



def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("RecipeUpload", RecipeUpload)
