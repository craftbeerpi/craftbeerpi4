from core.api.decorator import on_event
from core.controller.notification_controller import NotificationController
from core.craftbeerpi import CraftBeerPi




cbpi = CraftBeerPi()
cbpi.setup()
cbpi.start()