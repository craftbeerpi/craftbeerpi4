import logging


import aiohttp


class SystemController:

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.service = cbpi.actor
        self.logger = logging.getLogger(__name__)

        self.cbpi.app.on_startup.append(self.check_for_update)


    async def check_for_update(self, app):
        try:
            timeout = aiohttp.ClientTimeout(total=1)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post('http://localhost:2202/check', json=dict(version=app["cbpi"].version)) as resp:
                    if (resp.status == 200):
                        data = await resp.json()
                        if data.get("version") != self.cbpi.version:
                            self.logger.info("Version Check: Newer Version exists")
                        else:
                            self.logger.info("Version Check: You are up to date")
        except:
            self.logger.warning("Version Check: Can't check for update")



