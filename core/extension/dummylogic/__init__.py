import asyncio

from core.api import Property, on_event
from core.api.kettle_logic import CBPiKettleLogic


class CustomLogic(CBPiKettleLogic):

    test = Property.Number(label="Test")


    running = True


    async def wait_for_event(self, topic, timeout=None):


        future_obj = self.cbpi.app.loop.create_future()

        async def callback(id, **kwargs):
            print("---------------------------------- CALLBACK ----------------")
            print(kwargs)



            if int(id) == 1:
                self.cbpi.bus.unregister(callback)
                future_obj.set_result("HELLO")
            elif int(id) == 2:
                self.cbpi.bus.unregister(callback)
            else:
                print("ID", id)



        print("TOPIC", topic)
        self.cbpi.bus.register(topic=topic, method=callback)

        if timeout is not None:

            try:
                print("----> WAIT FOR FUTURE")
                await asyncio.wait_for(future_obj, timeout=10.0)
                print("------> RETURN RESULT")
                return future_obj.result()
            except asyncio.TimeoutError:
                print('timeout!')
        else:
            print("----> WAIT FOR FUTURE")
            await future_obj
            return future_obj.result()



    async def run(self):

        result = await self.wait_for_event("actor/+/on")
        print("THE RESULT", result)


        '''
        while self.running:
            
            
            print("RUN", self.test)
            value = await self.cbpi.sensor.get_value(1)
            print(value)
            if value >= 10:
                break
            await asyncio.sleep(1)
        '''
        print("STOP LOGIC")

def setup(cbpi):

    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server
    
    :param cbpi: the cbpi core 
    :return: 
    '''

    cbpi.plugin.register("CustomKettleLogic", CustomLogic)
