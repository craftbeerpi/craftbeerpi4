from cbpi.controller.basic_controller import BasicController

class SensorController(BasicController):
    def __init__(self, cbpi):
        super(SensorController, self).__init__(cbpi, "sensor.json")
