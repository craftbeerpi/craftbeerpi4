REST API
========

The REST API is document by using Swagger.IO.
After startup of the server the API documentation is available under:

::

    http://<SERVER_IP>:<PORT>/api/doc

.. swaggerv2doc:: http://0.0.0.0:8080/api/doc/swagger.json


WebSocket API
=============

WebSocket client can be connected to the following endpoint:

::

    http://<SERVER_IP>:<PORT>/ws

I recommend to use Dark WebSocket Terminal for testing. At the moment the WebSocket API is just pushing data.

.. note::
    Currently Security is not enabled. That means you need no password to connect to th Web APIs
