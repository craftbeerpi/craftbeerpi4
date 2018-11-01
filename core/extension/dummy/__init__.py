from core.database.model import ActorModel
from core.api.decorator import action, background_task
from core.api.property import Property


from core.api.actor import CBPiActor
import logging


class MyActor(CBPiActor):

    name = Property.Number(label="Test")
    name1 = Property.Text(label="Test")
    name2 = Property.Kettle(label="Test")

    @background_task("s1", interval=2)
    async def bg_job(self):
        print("WOOH BG")

    @action(key="name", parameters={})
    def myAction(self):
        pass

    def state(self):
        super().state()

    def off(self):
        super().off()

    def on(self, power=100):
        super().on(power)

    def __init__(self,cbpi=None):

        if cbpi is None:
            return

        self.cfg = self.load_config()
        print(self.cfg)
        self.logger = logging.getLogger(__file__)
        logging.basicConfig(level=logging.INFO)

        self.logger.info("########WOOHOO MY ACTOR")
        self.cbpi = cbpi


def setup(cbpi):

    cbpi.actor.register("MyActor", MyActor)