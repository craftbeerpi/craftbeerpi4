import logging

from aiohttp import web

from core.api.decorator import request_mapping
from core.utils.utils import json_dumps


class HttpAPI():
    def __init__(self, cbpi):
        self.logger = logging.getLogger(__name__)
        self.cbpi = cbpi

    @request_mapping(path="/", auth_required=False)
    async def http_get_all(self, request):
        """
                    ---
                    description: This end-point allow to test that service is up.
                    tags:
                    - REST API
                    produces:
                    - application/json
                    responses:
                        "200":
                            description: successful operation. Return "pong" text
                        "405":
                            description: invalid HTTP Method
                    """
        return web.json_response(await self.get_all(force_db_update=True), dumps=json_dumps)

    @request_mapping(path="/{id:\d+}", auth_required=False)
    async def http_get_one(self, request):
        """
                    ---
                    description: This end-point allow to test that service is up.
                    tags:
                    - REST API
                    produces:
                    - application/json
                    parameters:
                    - name: "id"
                      in: "path"
                      description: "ID of object to return"
                      required: true
                      type: "integer"
                      format: "int64"
                    responses:
                        "200":
                            description: successful operation. Return "pong" text
                        "405":
                            description: invalid HTTP Method
                    """
        id = int(request.match_info['id'])
        return web.json_response(await self.get_one(id), dumps=json_dumps)

    @request_mapping(path="/", method="POST", auth_required=False)
    async def http_add(self, request):
        """
                    ---
                    description: This end-point allow to test that service is up.
                    tags:
                    - REST API
                    produces:
                    - application/json
                    responses:
                        "200":
                            description: successful operation. Return "pong" text
                        "405":
                            description: invalid HTTP Method
                    """
        data = await request.json()
        obj = await self.add(**data)
        return web.json_response(obj, dumps=json_dumps)

    @request_mapping(path="/{id}", method="PUT", auth_required=False)
    async def http_update(self, request):
        """
                    ---
                    description: This end-point allow to test that service is up.
                    tags:
                    - REST API
                    produces:
                    - application/json
                    parameters:
                    - in: body
                      name: body
                      description: Created user object
                      required: false
                      schema:
                        type: object
                        properties:
                          id:
                            type: integer
                            format: int64           
                    responses:
                        "200":
                            description: successful operation. Return "pong" text
                        "405":
                            description: invalid HTTP Method
                    """
        id = request.match_info['id']
        data = await request.json()
        obj = await self.update(id, data)
        return web.json_response(obj, dumps=json_dumps)

    @request_mapping(path="/{id}", method="DELETE", auth_required=False)
    async def http_delete_one(self, request):
        """
                    ---
                    description: This end-point allow to test that service is up.
                    tags:
                    - REST API
                    produces:
                    - text/plain
                    responses:
                        "200":
                            description: successful operation. Return "pong" text
                        "405":
                            description: invalid HTTP Method
                    """
        id = request.match_info['id']
        await self.delete(id)
        return web.Response(str=204)
