from core.controller.crud_controller import CRUDController
from core.database.model import ConfigModel


class ConfigController(CRUDController):

    '''
    The main actor controller
    '''
    model = ConfigModel

    def __init__(self, cbpi):
        super(ConfigController, self).__init__(cbpi)
        self.cbpi = cbpi

        self.cbpi.register(self, "/config")


