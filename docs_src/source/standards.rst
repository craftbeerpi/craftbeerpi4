Standard & Guidelines
=====================

Python
^^^^^^

CraftBeerPi 4.x is based on Pyhton 3.7x. as main frameworks is `aiohttp` used.

* aioHTTP https://aiohttp.readthedocs.io/en/stable/

EventBus
--------

One core concept of CraftBeerPi 4.x is the EventBus.
It should be avoided to call method on a controller directly. Events should be fired and listener methods should be used.
This makes sure that all components are loosely coupled. New plugins can listen on events and extend or change the functionality easily.

Here an example how to fire an event

.. code-block:: python

  cbpi.bus.fire(topic="notification/hello", key="hello", message="Hello World")


Here an example how listen on an event.

.. code-block:: python

  @on_event(topic="actor/+/switch/on")
  def listener(self, id , power=100, **kwargs) -> None:
     pass


.. note::

  It's imporante to add **kwargs as parameter to the listening method. This makes sure that maybe addtional event paramenter are not causing an exception.


Web User Interface
^^^^^^^^^^^^^^^^^^
The Web UI is based on ReactJS + Redux.
The build process is based on webpack and bable.

* ReactJS: https://reactjs.org/
* Redux: https://redux.js.org/
* WebPack: https://webpack.js.org/
* Babel: https://babeljs.io

REST API
^^^^^^^^
The REST API of CraftBeerPi is documented using Swagger.io
After server startup you can find the API documentaiton under: `http://<IP_ADDRESS>:<PORT>/api/doc`

To generate the swagger file `aiohttp-swagger` is used. for more information see: https://aiohttp-swagger.readthedocs.io/en/latest/


