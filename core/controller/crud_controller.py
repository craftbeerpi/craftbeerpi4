class CRUDController(object):


    cache = {}
    caching = True

    def __init__(self, cbpi):
        self.cbpi = cbpi
        self.cache = {}

    async def init(self):
        '''
        
        :return: 
        '''
        if self.caching is True:
            self.cache = await self.model.get_all()

    async def get_all(self, force_db_update=False):
        '''
        
        :param force_db_update: 
        :return: 
        '''
        if self.caching is False or force_db_update:
            self.cache = await self.model.get_all()

        return self.cache

    async def get_one(self, id):
        '''
        
        :param id: 
        :return: 
        '''
        return self.cache.get(id)

    async def _pre_add_callback(self, data):
        '''
        
        :param data: 
        :return: 
        '''
        pass

    async def _post_add_callback(self, m):
        '''
        
        :param m: 
        :return: 
        '''
        pass

    async def add(self, **data):
        '''
        
        :param data: 
        :return: 
        '''
        await self._pre_add_callback(data)
        m = await self.model.insert(**data)
        await self._post_add_callback(m)
        self.cache[m.id] = m
        return m

    async def _pre_update_callback(self, m):
        pass

    async def _post_update_callback(self, m):
        pass

    async def update(self, id, data):
        '''
        
        :param id: 
        :param data: 
        :return: 
        '''
        id = int(id)
        data["id"] = id

        try:
            ### DELETE INSTANCE BEFORE UPDATE
            del data["instance"]
        except:
            pass

        if self.caching is True:
            await self._pre_update_callback(self.cache[id])
            self.cache[id].__dict__.update(**data)
            m = await self.model.update(**self.cache[id].__dict__)
            await self._post_update_callback(m)
        else:
            m = await self.model.update(**data)

        return m



    async def _pre_delete_callback(self, m):
        '''
        
        :param m: 
        :return: 
        '''
        pass

    async def _post_delete_callback(self, id):
        '''
        
        :param id: 
        :return: 
        '''
        pass

    async def delete(self, id):

        '''
        
        :param id: 
        :return: 
        '''
        await self._pre_delete_callback(id)
        m = await self.model.delete(id)
        await self._post_delete_callback(id)
        try:
            if self.caching is True:
                del self.cache[id]
        except Exception as e:
            pass

        #self.cbpi.push("DELETE_%s" % self.key, id)

    async def delete_all(self):
        '''
        
        :return: 
        '''
        self.model.delete_all()
        if self.caching is True:
            self.cache = {}
        #self.cbpi.push_ws("DELETE_ALL_%s" % self.key, None)