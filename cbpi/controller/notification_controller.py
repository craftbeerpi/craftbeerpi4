import asyncio
from email import message
from cbpi.api.dataclasses import NotificationType
from cbpi.api import *
import logging
import shortuuid
class NotificationController:

    def __init__(self, cbpi):
        '''
        :param cbpi: craftbeerpi object
        '''
        self.cbpi = cbpi
        self.logger = logging.getLogger(__name__)
        logging.root.addFilter(self.notify_log_event)
        self.callback_cache = {}    
        self.listener = {}
    
    def notify_log_event(self, record):
        NOTIFY_ON_ERROR = self.cbpi.config.get("NOTIFY_ON_ERROR", "No")
        if NOTIFY_ON_ERROR == "Yes":
            try:
                if record.levelno > 20:
                    # on log events higher then INFO we want to notify all clients
                    type = NotificationType.WARNING
                    if record.levelno > 30:
                        type = NotificationType.ERROR
                    self.cbpi.notify(title=f"{record.levelname}", message=record.msg, type = type)
            except Exception as e:
                pass
            finally:
                return True
        return True
    
    def add_listener(self, method):
        listener_id = shortuuid.uuid()
        self.listener[listener_id] = method
        return listener_id

    def remove_listener(self, listener_id):
        try:
            del self.listener[listener_id] 
        except:
            self.logger.error("Failed to remove listener {}".format(listener_id))

    async def _call_listener(self, title, message, type, action):
        for id, method in self.listener.items():
            #print(id, method)
            asyncio.create_task(method(self.cbpi, title, message, type, action ))


    def notify(self, title, message: str, type: NotificationType = NotificationType.INFO, action=[], timeout: int=5000) -> None:
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
        self.cbpi.ws.send(dict(id=notifcation_id, topic="notifiaction", type=type.value, title=title, message=message, action=actions, timeout=timeout))
        data = dict(type=type.value, title=title, message=message, action=actions, timeout=timeout)
        self.cbpi.push_update(topic="cbpi/notification", data=data)
        asyncio.create_task(self._call_listener(title, message, type, action))


    def notify_callback(self, notification_id, action_id) -> None:
        try:
            action = next((item for item in self.callback_cache[notification_id]  if item.id == action_id), None)
            if action.method is not None:
                asyncio.create_task(action.method())
            del self.callback_cache[notification_id]
        except Exception as e:
            self.logger.error("Failed to call notificatoin callback")
        