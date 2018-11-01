from core.database.model import ActorModel
from core.api.decorator import action, background_task
from core.api.property import Property
print("##################")

from core.api.actor import Actor
import logging


class MyActor(Actor):


    name = Property.Number(label="Test")
    name1 = Property.Text(label="Test")
    name2 = Property.Kettle(label="Test")

    @background_task("s1", interval=2)
    async def bg_job(self):
        print("WOOH BG")

    @action(key="name", parameters={})
    def myAction(self):
        print("HALLO")

    def state(self):
        super().state()

    def off(self):
        super().off()

    def on(self, power=100):
        super().on(power)

    def __init__(self):
        pass

    def __init__(self, core=None):
        self.logger = logging.getLogger(__name__)
        self.logger.info("WOOHOO MY ACTOR")
        self.core = None


def setup(cbpi):

    cbpi.actor.register("MyActor", MyActor)