import inspect
import logging

import asyncio


class EventBus(object):




    class Node(object):
        __slots__ = '_children', '_content'

        def __init__(self):
            self._children = {}
            self._content = None



    class Content(object):
        def __init__(self, parent, topic, method, once):

            self.parent = parent
            self.method = method
            self.name = method.__name__
            self.once = once
            self.topic = topic

    def register(self, topic, method, once=False):
        print("REGISTER", topic, method)
        if method in self.registry:
            raise RuntimeError("Method %s already registerd. Please unregister first!" % method.__name__)
        self.logger.info("Topic %s", topic)

        node = self._root
        for sym in topic.split('/'):
            node = node._children.setdefault(sym, self.Node())

        if not isinstance(node._content, list):
            node._content = []


        c = self.Content(node, topic, method, once)


        node._content.append(c)
        print(c, node._content, topic)
        self.registry[method] = c



    def get_callbacks(self, key):
        try:
            node = self._root
            for sym in key.split('/'):
                node = node._children[sym]
            if node._content is None:
                raise KeyError(key)
            return node._content
        except KeyError:
            raise KeyError(key)


    def unregister(self, method):
        self.logger.info("Unregister %s", method.__name__)
        if method in self.registry:
            content = self.registry[method]
            clean_idx = None
            for idx, content_obj in enumerate(content.parent._content):
                if method == content_obj.method:
                    clean_idx = idx
                    break
            if clean_idx is not None:
                del content.parent._content[clean_idx]

    '''
    def unregister(self, key, method):
        lst = []
        try:
            parent, node = None, self._root
            for k in key.split('/'):
                parent, node = node, node._children[k]
                lst.append((parent, k, node))
        except KeyError:
            raise KeyError(key)
        else:  # cleanup
            for parent, k, node in reversed(lst):
                if node._children or node._content is not None:
                    break
                del parent._children[k]
    '''

    def __init__(self, cbpi):
        self.logger = logging.getLogger(__name__)
        self._root = self.Node()
        self.registry = {}
        self.docs = {}
        self.cbpi = cbpi

    def fire(self, topic: str, **kwargs) -> None:
        print("#### FIRE", topic)
        self.logger.info("EMIT EVENT %s", topic)

        cleanup_methods = []
        for content_array in self.iter_match(topic):

            print(content_array)
            cleanup = []
            for idx, content_obj in enumerate(content_array):
                print("#################")

                print("TOPIC", content_obj.method, content_obj.topic)
                print("#################")
                if inspect.iscoroutinefunction(content_obj.method):
                    self.cbpi.app.loop.create_task(content_obj.method(**kwargs, topic = topic))
                else:
                    content_obj.method(**kwargs, topic = topic)

                if content_obj.once is True:
                    cleanup.append(idx)
            for idx in cleanup:
                del content_array[idx]


        print(self._root)
        print("#### FIRE END ######")


    def iter_match(self, topic):

        lst = topic.split('/')
        normal = not topic.startswith('$')

        def rec(node, i=0):
            if i == len(lst):
                if node._content is not None:
                    yield node._content
            else:
                part = lst[i]
                if part in node._children:
                    for content in rec(node._children[part], i + 1):
                        yield content
                if '+' in node._children and (normal or i > 0):
                    for content in rec(node._children['+'], i + 1):
                        yield content
            if '#' in node._children and (normal or i > 0):
                content = node._children['#']._content
                if content is not None:
                    yield content

        return rec(self._root)
