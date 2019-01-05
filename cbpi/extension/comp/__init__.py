import os

from aiohttp import web

from cbpi.api import *
from cbpi.controller.crud_controller import CRUDController
from cbpi.database.orm_framework import DBModel
from cbpi.http_endpoints.http_curd_endpoints import HttpCrudEndpoints


class DummyModel(DBModel):
    '''
    Cumstom Data Model which will is stored in the database
    '''
    __fields__ = ["name"]
    __table_name__ = "dummy"


class MyComp(CBPiExtension, CRUDController, HttpCrudEndpoints):
    model = DummyModel

    def __init__(self, cbpi):
        '''
        Initializer
        
        :param cbpi: 
        '''


        self.cbpi = cbpi
        # register component for http, events
        # In addtion the sub folder static is exposed to access static content via http
        self.cbpi.register(self, "/dummy", static=os.path.join(os.path.dirname(__file__), "static"))


    @on_event(topic="actor/#")
    async def listen(self, **kwargs):
        pass


    @on_event(topic="kettle/+/automatic")
    async def listen2(self, **kwargs):


        await self.cbpi.bus.fire(topic="actor/%s/toggle" % 1, id=1)


def setup(cbpi):
    '''
    Setup method is invoked during startup
    
    :param cbpi: the cbpi core object
    :return: 
    '''
    # regsiter the component to the core
    cbpi.plugin.register("MyComp", MyComp)
    pass