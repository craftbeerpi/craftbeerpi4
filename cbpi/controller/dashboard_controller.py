import logging

from voluptuous import Schema, MultipleInvalid

from cbpi.controller.crud_controller import CRUDController
from cbpi.database.model import DashboardModel, DashboardContentModel


class DashboardController(CRUDController):

    model = DashboardModel
    name = "Dashboard"

    def __init__(self, cbpi):
        super(DashboardController, self).__init__(cbpi)
        self.cbpi = cbpi
        self.logger = logging.getLogger(__name__)
        self.cbpi.register(self)

    def get_state(self):
        return dict(items=self.cache)

    async def get_content(self, dashboard_id):
        return await DashboardContentModel.get_by_dashboard_id(dashboard_id)

    async def add_content(self, data):
        return await DashboardContentModel.insert(**data)

    async def delete_content(self, content_id):
        await DashboardContentModel.delete(content_id)

    async def move_content(self,content_id, x, y):
        await DashboardContentModel.update_coordinates(content_id, x, y)
