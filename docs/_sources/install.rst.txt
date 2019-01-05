============
Installation
============

Please make sure that Python 3.5 is installed.
`Rapsbian Stretch <https://www.raspberrypi.org/downloads/raspbian//>`_ is required at least.
It will also run on MacOS


Download and Installation
=========================

::

    $ sudo pip install -i https://test.pypi.org/simple/ cbpi

Further version can be found on PiPy: https://test.pypi.org/project/cbpi/

.. note::
    All dependencies will be installed automatically. The installation will add the command "cbpi" to your shell.

To uninstall just remove the package via pip.

::

    $ sudo pip uninstall cbpi

Run the Server
==============

To start CraftBeerPi just run the following command in your shell
::

    $ cbpi


During the first startup a `config` and `logs` folder gets created in the directory from where the `$ cbpi` in called
PIP Website: https://test.pypi.org/project/cbpi/


Update CraftBeerPi
==================

That's super easy. Just run again with upgrade option
::
    $ sudo pip install -i https://test.pypi.org/simple/ cbpi --upgrade


Install plugins
===============

Plugins are normal Python Pip packages.

Install
::

    $ sudo pip install -i https://test.pypi.org/simple/ CBPiActor1

Uninstall

::

    $ pip uninstall CBPiActor1


