import logging

from core.helper.utils import load_config as load
logger = logging.getLogger(__file__)
logging.basicConfig(level=logging.INFO)

class CBPiExtension():

    def load_config(self):


        path = os.path.dirname(sys.modules[self.__class__.__module__].__file__)
        try:
            return load("%s/config.yaml" % path)
        except:
            logger.warning("Faild to load config %s/config.yaml" % path)
