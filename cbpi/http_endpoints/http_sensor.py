from cbpi.api import request_mapping

from cbpi.http_endpoints.http_curd_endpoints import HttpCrudEndpoints


class SensorHttpEndpoints(HttpCrudEndpoints):

    def __init__(self, cbpi):
        super().__init__(cbpi)
        self.controller = cbpi.sensor
        self.cbpi.register(self, "/sensor")

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
