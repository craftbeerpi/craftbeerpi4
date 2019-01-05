import logging
import os
import sys

import yaml

__all__ = ["CBPiExtension"]



logger = logging.getLogger(__file__)



class CBPiExtension():

    def init(self):
        pass

    def stop(self):
        pass

    def __init__(self, *args, **kwds):

        for a in kwds:
            logger.debug("Parameter: %s Value: %s" % ( a, kwds.get(a)))
            super(CBPiExtension, self).__setattr__(a, kwds.get(a))
        self.cbpi = kwds.get("cbpi")
        self.id = kwds.get("id")
        self.value = None
        self.__dirty = False

    def __setattr__(self, name, value):

        if name != "_CBPiExtension__dirty":
            self.__dirty = True
            super(CBPiExtension, self).__setattr__(name, value)
        else:
            super(CBPiExtension, self).__setattr__(name, value)

    def load_config(self):

        path = os.path.dirname(sys.modules[self.__class__.__module__].__file__)

        try:
            with open("%s/config.yaml" % path, 'rt') as f:
                data = yaml.load(f)

            return data
        except:
            logger.warning("Faild to load config %s/config.yaml" % path)



