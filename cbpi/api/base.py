from abc import abstractmethod, ABCMeta
import asyncio
from cbpi.api.config import ConfigType
import time

import logging


class CBPiBase(metaclass=ABCMeta):

    def get_static_config_value(self,name,default):
        return self.cbpi.static_config.get(name, default)

    def get_config_value(self,name,default):
        return self.cbpi.config.get(name, default=default)

    async def set_config_value(self,name,value):
        return await self.cbpi.config.set(name,value)

    async def add_config_value(self, name, value, type: ConfigType, description, options=None):
        await self.cbpi.add(name, value, type, description, options=None)

    def get_kettle(self,id):
        return self.cbpi.kettle.find_by_id(id)

    def get_kettle_target_temp(self,id):
        return self.cbpi.kettle.find_by_id(id).target_temp

    async def set_target_temp(self,id, temp):
        await self.cbpi.kettle.set_target_temp(id, temp)
    
    def get_fermenter(self,id):
        return self.cbpi.fermenter.find_by_id(id)

    def get_fermenter_target_temp(self,id):
        return self.cbpi.fermenter.find_by_id(id).target_temp

    async def set_fermenter_target_temp(self,id, temp):
        await self.cbpi.fermenter.set_target_temp(id, temp)

    def get_sensor(self,id):
        return self.cbpi.sensor.find_by_id(id)
    
    def get_sensor_value(self,id):
        
        return self.cbpi.sensor.get_sensor_value(id)

    def get_actor(self,id):
        return self.cbpi.actor.find_by_id(id)

    def get_actor_state(self,id):
        try:
            actor = self.cbpi.actor.find_by_id(id)
            return actor.get("instance").get_state()
        except:
            logging.error("Faild to read actor state in step - actor {}".format(id))
            return None

    async def actor_on(self,id):
        
        try:
            await self.cbpi.actor.on(id)
        except Exception as e:
            pass

    async def actor_off(self,id):
        try:
            await self.cbpi.actor.off(id)
        except Exception as e:
            pass


