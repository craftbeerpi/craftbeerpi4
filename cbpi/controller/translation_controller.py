import logging

from database.model import TranslationModel


class TranslationController(object):


    def __init__(self, cbpi):
        self.cbpi = cbpi
        self._cache = {}
        self.logger = logging.getLogger(__name__)

    async def init(self):
        self._cache = await TranslationModel.get_all()
        print(self._cache)


    def get_all(self):
        return self._cache

    async def add_key(self, locale, key):

        try:
            if locale not in self._cache or key not in self._cache[locale]:
                await TranslationModel.add_key(locale, key)
                self._cache = await TranslationModel.get_all()
        except Exception as e:
            self.logger.error("Error during adding translation key %s - %s - %s" % (key, locale, str(e)))
