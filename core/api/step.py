class Step(object):

    def __init__(self, key=None, cbpi=None):
        self.cbpi = cbpi
        self.id = key

    async def run(self):
        pass

    def stop(self):
        pass