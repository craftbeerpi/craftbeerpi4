from aiohttp import web

from core.api.decorator import on_event, request_mapping
from core.api.extension import CBPiExtension
from core.controller.crud_controller import CRUDController
from core.database.orm_framework import DBModel
from core.http_endpoints.http_api import HttpAPI


class DummyModel(DBModel):
    __fields__ = ["name"]
    __table_name__ = "dummy"


class MyComp(CBPiExtension, CRUDController, HttpAPI):
    model = DummyModel

    def __init__(self, cbpi):
        '''
        Initializer
        
        :param cbpi: 
        '''
        self.cbpi = cbpi
        # register for bus events
        self.cbpi.register(self, "/dummy", static="./core/extension/comp/static")


    @on_event(topic="actor/#")
    def listen(self, **kwargs):
        print("Test", kwargs)

    @on_event(topic="kettle/+/automatic")
    def listen2(self, **kwargs):
        print("HANDLE AUTOMATIC", kwargs)

        self.cbpi.bus.fire(topic="actor/%s/toggle" % 1, id=1)




def setup(cbpi):
    '''
    Setup method is invoked during startup
    
    :param cbpi: the cbpi core object
    :return: 
    '''
    # regsiter the component to the core
    cbpi.plugin.register("MyComp", MyComp)
    pass