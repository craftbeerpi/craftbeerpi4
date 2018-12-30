import asyncio
import inspect
import logging


class CBPiEventBus(object):
    class Node(object):
        __slots__ = '_children', '_content'

        def __init__(self):
            self._children = {}
            self._content = None

    class Content(object):
        def __init__(self, parent, topic, method, once, supports_future=False):
            self.parent = parent
            self.method = method
            self.name = method.__name__
            self.once = once
            self.topic = topic
            self.supports_future = supports_future

    class Result():

        def __init__(self, result, timeout):
            self.result = result
            self.timeout = timeout

    class ResultContainer():

        def __init__(self, results, timeout=False):
            self.results = {}
            self.timeout = timeout
            for key, value in results.items():
                if value.done() is True:
                    self.results[key] = CBPiEventBus.Result(value.result(), True)
                else:
                    self.results[key] = CBPiEventBus.Result(None, False)



    def register(self, topic, method, once=False):



        if method in self.registry:
            raise RuntimeError("Method %s already registerd. Please unregister first!" % method.__name__)
        self.logger.info("Topic %s", topic)
        node = self._root
        for sym in topic.split('/'):
            node = node._children.setdefault(sym, self.Node())

        if not isinstance(node._content, list):
            node._content = []

        sig = inspect.signature(method)


        if "future" in sig.parameters:
            supports_future = True
        else:
            supports_future = False
        c = self.Content(node, topic, method, once, supports_future)
        node._content.append(c)
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

    def __init__(self, loop, cbpi):
        self.logger = logging.getLogger(__name__)
        self.cbpi = cbpi
        self._root = self.Node()
        self.registry = {}
        self.docs = {}
        if loop is not None:
            self.loop = loop
        else:
            self.loop = asyncio.get_event_loop()



    def sync_fire(self,topic: str,timeout=1, **kwargs):
        self.loop.create_task(self.fire(topic=topic, timeout=timeout, **kwargs))

    async def fire(self, topic: str, timeout=1, **kwargs):

        futures = {}

        async def wait(futures):
            if(len(futures) > 0):
                await asyncio.wait(futures.values())


        for e in self.iter_match(topic):
            content_array = e
            keep_idx = []
            for idx, content_obj in enumerate(content_array):

                if inspect.iscoroutinefunction(content_obj.method):
                    if content_obj.supports_future is True:

                        fut = self.loop.create_future()

                        futures["%s.%s" % (content_obj.method.__module__, content_obj.name)] = fut
                        self.loop.create_task(content_obj.method(**kwargs, topic = topic, future=fut))

                    else:
                        self.loop.create_task(content_obj.method(**kwargs, topic=topic))
                else:
                    # only asnyc
                    pass
                if content_obj.once is False:
                    keep_idx.append(idx)

            # FILTER only elements with are required
            if len(keep_idx) < len(e):
                e[0].parent._content = [e[0].parent._content[i] for i in keep_idx]

        if timeout is not None:
            try:
                await asyncio.wait_for(wait(futures), timeout=timeout)
                is_timedout = False
            except asyncio.TimeoutError:
                is_timedout = True
            return self.ResultContainer(futures, is_timedout)


    def dump(self):
        def rec(node, i=0):
            result = []
            if node._content is not None:
                for c in node._content:
                    result.append(dict(topic=c.topic, method=c.method.__name__, path=c.method.__module__, once=c.once))

            if node._children is not None:
                for c in node._children:
                    result = result + rec(node._children[c], i + 1)
            return result

        result = rec(self._root)

        return result

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
