import asyncio
import logging
import shortuuid
class NotificationController:

    def __init__(self, cbpi):
        '''

        :param cbpi: craftbeerpi object
        '''
        self.cbpi = cbpi
        self.logger = logging.getLogger(__name__)
        self.callback_cache = {}

    def notify(self, title, message: str, type: str = "info", action=[]) -> None:
        '''
        This is a convinience method to send notification to the client
        
        :param key: notification key
        :param message: notification message
        :param type: notification type (info,warning,danger,successs)
        :return: 
        '''
        notifcation_id = shortuuid.uuid()

        def prepare_action(item):
            item.id = shortuuid.uuid()
            return item.to_dict()

        actions = list(map(lambda item: prepare_action(item), action))
        self.callback_cache[notifcation_id] = action
        self.cbpi.ws.send(dict(id=notifcation_id, topic="notifiaction", type=type, title=title, message=message, action=actions))

    def notify_callback(self, notification_id, action_id) -> None:
        try:
            action = next((item for item in self.callback_cache[notification_id]  if item.id == action_id), None)
            if action.method is not None:
                asyncio.create_task(action.method())
            del self.callback_cache[notification_id]
        except Exception as e:
            self.logger.error("Faild to call notificatoin callback")
        