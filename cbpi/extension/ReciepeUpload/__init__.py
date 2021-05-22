
# -*- coding: utf-8 -*-
import os
import pathlib
import aiohttp
from aiohttp import web
import logging
from unittest.mock import MagicMock, patch
import asyncio
from cbpi.api import *
from voluptuous.schema_builder import message
from cbpi.api.dataclasses import NotificationAction, NotificationType
from cbpi.controller.kettle_controller import KettleController
from cbpi.api.base import CBPiBase
from cbpi.api.config import ConfigType
import json
import webbrowser

logger = logging.getLogger(__name__)

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

def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("RecipeUpload", RecipeUpload)
