Brewing Step
============



StepController
^^^^^^^^^^^^^^^

.. autoclass:: core.controller.step_controller.StepController
  :members:

  :undoc-members:
  :show-inheritance:


CBPiSimpleStep
^^^^^^^^^^^^^^

.. autoclass:: core.api.step.CBPiSimpleStep
  :members:
  :undoc-members:
  :show-inheritance:


Custom Step
^^^^^^^^^^^

This is an example of a custom step. The Step class need to extend Simple step. In addtion at least the run_cycle method needs to be overwritten


.. literalinclude:: ../../core/extension/dummystep/__init__.py
   :caption: __init__.py
   :name: __init__-py
   :language: python
   :linenos:


config.yaml

.. literalinclude:: ../../core/extension/dummystep/config.yaml
   :language: yaml
   :linenos: