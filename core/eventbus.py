import logging


class EventBus(object):
    class Node(object):
        __slots__ = '_children', '_content'

        def __init__(self):
            self._children = {}
            self._content = None

    def register(self, key, value, doc=None):

        if doc is not None:
            self.docs[key] = doc
        self.logger.info("key %s", key)
        node = self._root
        for sym in key.split('/'):
            node = node._children.setdefault(sym, self.Node())

        if not isinstance(node._content, list):
            node._content = []
        node._content.append(value)

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

    def unregister(self, key, method=None):

        lst = []
        try:
            parent, node = None, self._root
            for k in key.split('/'):
                parent, node = node, node._children[k]
                lst.append((parent, k, node))
            # TODO
            print(node._content)
            if method is not None:
                node._content = None
            else:
                node._content = None
        except KeyError:
            raise KeyError(key)
        else:  # cleanup
            for parent, k, node in reversed(lst):
                if node._children or node._content is not None:
                    break
                del parent._children[k]

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._root = self.Node()
        self.docs = {}

    def fire(self, event: str, **kwargs) -> None:
        self.logger.info("EMIT EVENT %s", event)
        for methods in self.iter_match(event):
            for f in methods:

                f(**kwargs)

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
