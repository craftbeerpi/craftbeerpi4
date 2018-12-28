import asyncio

from cbpi_api import *

class CustomLogic(CBPiKettleLogic):

    test = Property.Number(label="Test")

    running = True


    async def wait_for_event(self, topic, callback=None, timeout=None):


        future_obj = self.cbpi.app.loop.create_future()

        async def default_callback(id, **kwargs):
            future_obj.set_result("HELLO")


        if callback is None:
            self.cbpi.bus.register(topic=topic, method=default_callback)
        else:
            callback.future = future_obj
            self.cbpi.bus.register(topic=topic, method=callback)

        if timeout is not None:

            try:

                await asyncio.wait_for(future_obj, timeout=timeout)

                return future_obj.result()
            except asyncio.TimeoutError:
                pass
        else:

            await future_obj
            return future_obj.result()



    async def run(self):


        async def my_callback(value, **kwargs):

            if value == 5:
                self.cbpi.bus.unregister(my_callback)
                kwargs["future"].set_result("AMAZING")
            else:
                pass

        result = await self.wait_for_event("sensor/1", callback=my_callback)



        '''
        while self.running:
            
            
            print("RUN", self.test)
            value = await self.cbpi.sensor.get_value(1)
            print(value)
            if value >= 10:
                break
            await asyncio.sleep(1)
        '''


def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("CustomKettleLogic", CustomLogic)
