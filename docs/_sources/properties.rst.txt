Properties
===========

Properties can be use in all extensions.
During the startup the server scans all extension for variables of type Property.
Theses properties are exposed to the user for configuration during run time.
For example the user can set the GPIO number or the 1Wire Id.



Typical example how to use properties in an actor module.

Custom Actor
^^^^^^^^^^^^^

.. literalinclude:: ../../cbpi/extension/dummyactor/__init__.py
   :caption: __init__.py
   :name: __init__-py
   :language: python
   :linenos:





.. autoclass:: cbpi.api.Property
  :members:
  :private-members:
  :undoc-members:


