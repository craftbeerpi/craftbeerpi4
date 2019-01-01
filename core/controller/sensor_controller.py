import json
import logging

from cbpi_api import request_mapping

from core.controller.crud_controller import CRUDController
from core.database.model import SensorModel
from core.http_endpoints.http_api import HttpAPI
from core.job.aiohttp import get_scheduler_from_app
from core.utils.encoder import ComplexEncoder


class SensorController(CRUDController, HttpAPI):

    model = SensorModel

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.cbpi.register(self, "/sensor")
        self.service = self
        self.types = {}
        self.logger = logging.getLogger(__name__)
        self.sensors = {}

    def info(self):
        return json.dumps(dict(name="SensorController", types=self.types), cls=ComplexEncoder)

    @request_mapping(path="/types", auth_required=False)
    async def get_types(self, request):
        """
        ---
        description: Get all sensor types
        tags:
        - Sensor
        responses:
            "200":
                description: successful operation
        """
        return await super().get_types(request)

    @request_mapping(path="/", auth_required=False)
    async def http_get_all(self, request):
        """

        ---
        description: Get all sensor
        tags:
        - Sensor
        responses:
            "204":
                description: successful operation
        """
        return await super().http_get_all(request)

    @request_mapping(path="/{id:\d+}", auth_required=False)
    async def http_get_one(self, request):
        """
        ---
        description: Get an sensor
        tags:
        - Sensor
        parameters:
        - name: "id"
          in: "path"
          description: "Sensor ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
            "405":
                description: invalid HTTP Met
        """
        return await super().http_get_one(request)

    @request_mapping(path="/", method="POST", auth_required=False)
    async def http_add(self, request):
        """
        ---
        description: Get one sensor
        tags:
        - Sensor
        parameters:
        - in: body
          name: body
          description: Created an sensor
          required: false
          schema:
            type: object
            properties:
              name:
                type: string
              type:
                type: string
              config:
                type: object
        responses:
            "204":
                description: successful operation
        """
        return await super().http_add(request)

    @request_mapping(path="/{id}", method="PUT", auth_required=False)
    async def http_update(self, request):
        """
        ---
        description: Update an sensor
        tags:
        - Sensor
        parameters:
        - name: "id"
          in: "path"
          description: "Sensor ID"
          required: true
          type: "integer"
          format: "int64"
        - in: body
          name: body
          description: Update an sensor
          required: false
          schema:
            type: object
            properties:
              name:
                type: string
              type:
                type: string
              config:
                type: object
        responses:
            "200":
                description: successful operation
        """
        return await super().http_update(request)

    @request_mapping(path="/{id}", method="DELETE", auth_required=False)
    async def http_delete_one(self, request):
        """
        ---
        description: Delete an sensor
        tags:
        - Sensor
        parameters:
        - name: "id"
          in: "path"
          description: "Sensor ID"
          required: true
          type: "integer"
          format: "int64"
        responses:
            "204":
                description: successful operation
        """
        return await super().http_delete_one(request)

    async def init(self):
        '''
        This method initializes all actors during startup. It creates actor instances

        :return: 
        '''
        await super(SensorController, self).init()
        for id, value in self.cache.items():
            await self.init_sensor(value)

    async def init_sensor(self, sensor):
        if sensor.type in self.types:
            cfg = sensor.config.copy()
            cfg.update(dict(cbpi=self.cbpi, id=sensor.id, name=sensor.name))
            clazz = self.types[sensor.type]["class"];
            self.cache[sensor.id].instance = clazz(**cfg)
            self.cache[sensor.id].instance.init()
            scheduler = get_scheduler_from_app(self.cbpi.app)
            self.cache[sensor.id].instance.job = await scheduler.spawn(self.cache[sensor.id].instance.run(self.cbpi), sensor.name, "sensor")
        else:
            self.logger.error("Sensor type '%s' not found (Available Sensor Types: %s)" % (sensor.type, ', '.join(self.types.keys())))

    async def stop_sensor(self, sensor):
        print("STOP", sensor.id)
        sensor.instance.stop()
        await self.cbpi.bus.fire(topic="sensor/%s/stopped" % sensor.id, id=sensor.id)


    async def get_value(self, sensor_id):
        sensor_id = int(sensor_id)
        return self.cache[sensor_id].instance.value

    async def _post_add_callback(self, m):
        '''

        :param m:
        :return:
        '''
        await self.init_sensor(m)
        pass

    async def _pre_delete_callback(self, sensor_id):
        if int(sensor_id) not in self.cache:
            return

        if self.cache[int(sensor_id)].instance is not None:
            await self.stop_sensor(self.cache[int(sensor_id)])

    async def _pre_update_callback(self, sensor):

        if sensor.instance is not None:
            await self.stop_sensor(sensor)

    async def _post_update_callback(self, sensor):
        self.init_sensor(sensor)