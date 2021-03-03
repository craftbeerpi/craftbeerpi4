
import asyncio
from cbpi.api.step import CBPiStep, StepResult
from cbpi.api.timer import Timer
from cbpi.api import *
import logging

@parameters([Property.Number(label="Timer", description="Time in Minutes", configurable=True), 
             Property.Number(label="Temp", configurable=True),
             Property.Sensor(label="Sensor"),
             Property.Kettle(label="Kettle")])
class MashStep(CBPiStep):

    @action(key="Custom RESET", parameters=[])
    async def custom_reset(self, **kwargs):
        self.summary = ""
        await self.push_update()
        

    @action(key="Custom Action", parameters=[Property.Number(label="Value", configurable=True)])
    async def custom_action(self, Value, **kwargs):
        self.summary = "VALUE FROM ACTION {}".format(Value)
        await self.push_update()
        self.cbpi.notify("ACTION 2 CALLED".format(Value))

    async def on_timer_done(self,timer):
        self.summary = ""
        await self.next()

    async def on_timer_update(self,timer, seconds):
        self.summary = Timer.format_time(seconds)
        await self.push_update()

    async def on_start(self):
        if self.timer is None:
            self.timer = Timer(int(self.props.Timer) *60 ,on_update=self.on_timer_update, on_done=self.on_timer_done)
        self.summary = "Waiting for Target Temp"
        await self.push_update()

    async def on_stop(self):
        await self.timer.stop()
        self.summary = ""
        await self.push_update()

    async def reset(self):
        self.summary = ""
        self.timer = Timer(int(self.props.Timer) *60 ,on_update=self.on_timer_update, on_done=self.on_timer_done)

    async def run(self):
        while True:
            await asyncio.sleep(1)
            sensor_value = self.get_sensor_value(self.props.Sensor)
            if sensor_value.get("value") >= int(self.props.Temp) and self.timer == None:
                self.timer.start()
        return StepResult.DONE

@parameters([Property.Number(label="Timer", description="Time in Minutes", configurable=True)])
class WaitStep(CBPiStep):

    @action(key="Custom Step Action", parameters=[])
    async def hello(self, **kwargs):
        print("ACTION")
        self.cbpi.notify("ACTION 1 CALLED")

    @action(key="Custom Step Action 2", parameters=[])
    async def hello2(self, **kwargs):
        print("ACTION2")
        self.cbpi.notify("ACTION 2 CALLED")

    async def on_timer_done(self,timer):
        self.summary = ""
        await self.next()

    async def on_timer_update(self,timer, seconds):
        self.summary = Timer.format_time(seconds)
        await self.push_update()

    async def on_start(self):
        if self.timer is None:
            self.timer = Timer(int(self.props.Timer) * 60,on_update=self.on_timer_update, on_done=self.on_timer_done)
        self.timer.start()

    async def on_stop(self):
        await self.timer.stop()
        self.summary = ""
        await self.push_update()

    async def reset(self):
        self.timer = Timer(int(self.props.Timer) * 60,on_update=self.on_timer_update, on_done=self.on_timer_done)

    async def run(self):
        while True:
            await asyncio.sleep(1)
        return StepResult.DONE

@parameters([Property.Number(label="Timer", description="Time in Minutes", configurable=True),
                Property.Actor(label="Actor")])
class ActorStep(CBPiStep):
    async def on_timer_done(self,timer):
        self.summary = ""
        await self.next()

    async def on_timer_update(self,timer, seconds):
        self.summary = Timer.format_time(seconds)
        await self.push_update()

    async def on_start(self):
        if self.timer is None:
            self.timer = Timer(int(self.props.Timer) * 60,on_update=self.on_timer_update, on_done=self.on_timer_done)
        self.timer.start()
        await self.actor_on(self.props.Actor)

    async def on_stop(self):
        await self.actor_off(self.props.Actor)
        await self.timer.stop()
        self.summary = ""
        await self.push_update()
        
    async def reset(self):
        self.timer = Timer(int(self.props.Timer) *60 ,on_update=self.on_timer_update, on_done=self.on_timer_done)

    async def run(self):

        while True:
            await asyncio.sleep(1)
        return StepResult.DONE


@parameters([Property.Number(label="Timer", description="Time in Minutes", configurable=True), 
             Property.Number(label="Temp", description="Boil temperature", configurable=True),
             Property.Sensor(label="Sensor"),
             Property.Kettle(label="Kettle")])
class BoilStep(CBPiStep):

    async def on_timer_done(self,timer):
        self.summary = ""
        await self.next()

    async def on_timer_update(self,timer, seconds):
        self.summary = Timer.format_time(seconds)
        await self.push_update()

    async def on_start(self):
        if self.timer is None:
            self.timer = Timer(int(self.props.Timer) *60 ,on_update=self.on_timer_update, on_done=self.on_timer_done)

        self.summary = "Waiting for Target Temp"
        await self.push_update()

    async def on_stop(self):
        await self.timer.stop()
        self.summary = ""
        await self.push_update()

    async def reset(self):
        self.timer = Timer(int(self.props.Timer) *60 ,on_update=self.on_timer_update, on_done=self.on_timer_done)

    @action("Start Timer", [])
    async def star_timer(self):
        self.cbpi.notify("Timer started")
        self.timer.start()

    async def run(self):
        while True:
            await asyncio.sleep(1)
            sensor_value = self.get_sensor_value(self.props.Sensor)
            if sensor_value is not None and sensor_value.get("value") >= int(self.props.Temp) and self.timer == None:
                self.timer.start()
        return StepResult.DONE

def setup(cbpi):
    '''
    This method is called by the server during startup 
    Here you need to register your plugins at the server

    :param cbpi: the cbpi core 
    :return: 
    '''    
    
    cbpi.plugin.register("BoilStep", BoilStep)
    cbpi.plugin.register("WaitStep", WaitStep)
    cbpi.plugin.register("MashStep", MashStep)
    cbpi.plugin.register("ActorStep", ActorStep)
    
    
    

    
