from cbpi.controller.basic_controller import BasicController
import logging

class SensorController(BasicController):
    def __init__(self, cbpi):
        super(SensorController, self).__init__(cbpi, "sensor.json")
        self.update_key = "sensorupdate"

    def create_dict(self, data):
        try:
            instance = data.get("instance")
            state = state=instance.get_state()
        except Exception as e:
            logging.error("Faild to crate actor dict {} ".format(e))
            state = dict() 

        return dict(name=data.get("name"), id=data.get("id"), type=data.get("type"), state=state,props=data.get("props", []))
        