class CRUDController(object):


    cache = {}
    caching = True

    def __init__(self, core):
        self.cbpi = core
        self.cache = {}

    async def init(self):
        if self.caching is True:
            self.cache = await self.model.get_all()

    async def get_all(self, force_db_update=False):

        if self.caching is False or force_db_update:
            self.cache = await self.model.get_all()

        return self.cache

    async def get_one(self, id):

        return self.cache.get(id)




    async def _pre_add_callback(self, data):
        pass

    async def _post_add_callback(self, m):
        pass

    async def add(self, **data):
        await self._pre_add_callback(data)
        m = await self.model.insert(**data)
        await self._post_add_callback(m)
        self.cache[m.id] = m
        return m

    async def _pre_update_callback(self, id):
        pass

    async def _post_update_callback(self, m):
        pass

    async def update(self, id, **data):

        await self._pre_update_callback(id)
        data["id"] = id
        try:
            del data["instance"]
        except:
            pass
        m = await self.model.update(**data)
        #self.core.push_ws("UPDATE_%s" % self.key, m)

        await self._post_update_callback(m)
        if self.caching is True:
            self.cache[m.id] = m
        return m

    async def _pre_delete_callback(self, m):
        pass

    async def _post_delete_callback(self, id):
        pass

    async def delete(self, id):
        await self._pre_delete_callback(id)
        m = await self.model.delete(id)
        await self._post_delete_callback(id)
        try:
            if self.caching is True:
                del self.cache[id]
        except Exception as e:
            pass

        #self.core.push("DELETE_%s" % self.key, id)

    async def delete_all(self):
        self.model.delete_all()
        if self.caching is True:
            self.cache = {}
        #self.core.push_ws("DELETE_ALL_%s" % self.key, None)