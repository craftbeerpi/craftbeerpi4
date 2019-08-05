import asyncio
import logging

from cbpi.job.aiohttp import setup, get_scheduler_from_app

logger = logging.getLogger(__name__)

class JobController(object):

    def __init__(self, cbpi):
        self.cbpi = cbpi

    async def init(self):
        await setup(self.cbpi.app, self.cbpi)

    def register_background_task(self, obj):
        '''
        This method parses all method for the @background_task decorator and registers the background job
        which will be launched during start up of the server

        :param obj: the object to parse
        :return:
        '''

        async def job_loop(app, name, interval, method):
            logger.info("Start Background Task %s Interval %s Method %s" % (name, interval, method))
            while True:
                logger.debug("Execute Task %s - interval(%s second(s)" % (name, interval))
                await asyncio.sleep(interval)
                await method()

        async def spawn_job(app):
            scheduler = get_scheduler_from_app(self.cbpi.app)
            for method in [getattr(obj, f) for f in dir(obj) if callable(getattr(obj, f)) and hasattr(getattr(obj, f), "background_task")]:
                name = method.__getattribute__("name")
                interval = method.__getattribute__("interval")
                job = await scheduler.spawn(job_loop(self.app, name, interval, method), name, "background")

        self.cbpi.app.on_startup.append(spawn_job)



    async def start_job(self, method, name, type):
        scheduler = get_scheduler_from_app(self.cbpi.app)
        return await scheduler.spawn(method, name, type)
