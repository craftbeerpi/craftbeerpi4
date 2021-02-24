
import asyncio
from cbpi.api.step import CBPiStep, StepResult
from cbpi.api.timer import Timer

from cbpi.api import *
import logging
import time

@parameters([Property.Number(label="Timer", description="Time in Minutes", configurable=True), 
             Property.Number(label="Temp", configurable=True),
             Property.Sensor(label="Sensor"),
             Property.Kettle(label="Kettle")])
class MashStep(CBPiStep):

    @action(key="Custom Step Action", parameters=[])
    async def hello(self, **kwargs):
        print("ACTION")

    @action(key="Custom Step Action 2", parameters=[])
    async def hello2(self, **kwargs):
        print("ACTION2")
        
    async def on_timer_done(self,timer):
        self.summary = ""
        await self.next()

    async def on_timer_update(self,timer, seconds):
        self.summary = Timer.format_time(seconds)
        await self.push_update()

    async def on_start(self):
        self.kettle = self.get_kettle(self.props.Kettle)
        self.kettle.target_temp = int(self.props.Temp)
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

    async def run(self):
        while True:
            await asyncio.sleep(1)
            sensor_value = self.get_sensor_value(self.props.Sensor)
            if sensor_value.get("value") >= int(self.props.Temp) and self.timer._task == None:
                self.timer.start()
        return StepResult.DONE

@parameters([Property.Number(label="Timer", description="Time in Minutes", configurable=True)])
class WaitStep(CBPiStep):

    @action(key="Custom Step Action", parameters=[])
    async def hello(self, **kwargs):
        print("ACTION")

    @action(key="Custom Step Action 2", parameters=[])
    async def hello2(self, **kwargs):
        print("ACTION2")

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
             Property.Kettle(label="Kettle"),
             Property.Select("First_Wort", options=["Yes","No"], description="First Wort Hop alert if set to Yes"),
             Property.Number("Hop_1", configurable = True, description="First Hop alert (minutes before finish)"),
             Property.Number("Hop_2", configurable = True, description="Second Hop alert (minutes before finish)"),
             Property.Number("Hop_3", configurable = True, description="Third Hop alert (minutes before finish)"),
             Property.Number("Hop_4", configurable = True, description="Fourth Hop alert (minutes before finish)"),
             Property.Number("Hop_5", configurable = True, description="Fifth Hop alert (minutes before finish)")])

class BM_BoilStep(CBPiStep):

    async def get_remaining_time(self):
        if self.timer.start_time != None:
            # self.remaining_time = self.timer.start_time+self.timer.timeout-time.time()
            self.remaining_time=self.timer.remaining_time
        else:
            self.remaining_time = None
        return self.remaining_time

    async def on_timer_done(self,timer):
        self.summary = ""
        await self.next()

    async def on_timer_update(self,timer, seconds):
        self.summary = Timer.format_time(seconds)
        await self.push_update()

    async def on_start(self):
        self.first_wort_hop_flag = False 
        self.first_wort_hop=self.props.First_Wort 
        self.hops_added=["","","","",""]

        self.kettle=self.get_kettle(self.props.Kettle)
        self.kettle.target_temp = int(self.props.Temp)

        if self.timer is None:
            self.timer = Timer(int(self.props.Timer) *60 ,on_update=self.on_timer_update, on_done=self.on_timer_done)

        self.summary = "Waiting for Target Temp"
        await self.push_update()

    async def check_hop_timer(self, number, value):
        if value is not None and self.hops_added[number-1] is not True:
            await self.get_remaining_time()
            if self.remaining_time != None and self.remaining_time <= (int(value) * 60 + 1):
                self.hops_added[number-1]= True
                self.cbpi.notify("Hop Alert. Please add Hop %s" % number)
                print("Hop Alert. Please add Hop %s" % number)

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
        if self.first_wort_hop_flag == False and self.first_wort_hop == "Yes":
            self.first_wort_hop_flag = True
            print("Add First Wort")
            self.cbpi.notify("First Wort Hop Addition! Please add hops for first wort")

        while True:
            await asyncio.sleep(1)
            sensor_value = self.get_sensor_value(self.props.Sensor)
            await self.get_remaining_time()
            if sensor_value is not None and sensor_value.get("value") >= int(self.props.Temp) and self.timer._task == None:
                self.timer.start()
            else:
                await self.check_hop_timer(1, self.props.Hop_1)
                await self.check_hop_timer(2, self.props.Hop_2)
                await self.check_hop_timer(3, self.props.Hop_3)
                await self.check_hop_timer(4, self.props.Hop_4)
                await self.check_hop_timer(5, self.props.Hop_5)
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
    
    
    

    
