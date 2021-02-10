from cbpi.controller.basic_controller import BasicController
import logging

class SensorController(BasicController):
    def __init__(self, cbpi):
        super(SensorController, self).__init__(cbpi, "sensor.json")
        self.update_key = "sensorupdate"

    def create_dict(self, data):
        try:
            instance = data.get("instance")
            state =instance.get_state()
        except Exception as e:
            logging.error("Faild to create sensor dict {} ".format(e))
            state = dict() 

        return dict(name=data.get("name"), id=data.get("id"), type=data.get("type"), state=state,props=data.get("props", []))
    
    def get_sensor_value(self, id):
        try:
            return self.find_by_id(id).get("instance").get_state()
        except Exception as e:
            logging.error("Faild read sensor value {} {} ".format(id, e))
            return None