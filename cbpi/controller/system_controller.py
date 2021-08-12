import logging
import os

import aiohttp


class SystemController:

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.service = cbpi.actor
        self.logger = logging.getLogger(__name__)

        self.cbpi.app.on_startup.append(self.check_for_update)


    async def check_for_update(self, app):
        pass


    async def restart(self):
        logging.info("RESTART")
        os.system('systemctl reboot') 
        pass

    async def shutdown(self):
        logging.info("SHUTDOWN")
        os.system('systemctl poweroff') 
        pass
