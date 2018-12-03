import asyncio

from core.api.step import Step


class CustomStep(Step):

    async def run(self):
        i = 0
        while i < 3:
            await asyncio.sleep(1)
            print("RUN STEP")
            i = i + 1


def setup(cbpi):
    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server

    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("CustomStep", CustomStep)
