class MQTTMatcher(object):


    class Node(object):
        __slots__ = '_children', '_content'

        def __init__(self):
            self._children = {}
            self._content = None


    def register(self, key, value):
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
        self._root = self.Node()

    def __setitem__(self, key, value):
        print("...",key, value)
        node = self._root
        for sym in key.split('/'):
            print(sym)
            node = node._children.setdefault(sym, self.Node())
            print(node)
        if not isinstance(node._content, list):
            #print("new array")
            node._content = []
        node._content.append(value)
        #node._content = value

    def __getitem__(self, key):
        try:
            node = self._root
            for sym in key.split('/'):
                node = node._children[sym]
            if node._content is None:
                raise KeyError(key)
            return node._content
        except KeyError:
            raise KeyError(key)
    '''
    
    def __delitem__(self, thekey):
        print("DELETE")

        if isinstance(thekey, tuple):
            key = thekey[1]
            methods = thekey[0]
            print(methods.__module__, methods.__name__)
        else:
            methods = None
            key = thekey

        lst = []
        try:
            parent, node = None, self._root
            for k in key.split('/'):
                 parent, node = node, node._children[k]
                 lst.append((parent, k, node))
            # TODO
            print(node._content)
            if methods is not None:

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
    '''
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


if __name__ == "__main__":
    m = MQTTMatcher()

    def test_name():
        print("actor/1/on")

    def test_name2():
        print("actor/2/on")

    def test_name3():
        print("actor/#")

    def test_name4():
        print("actor/+/on")



    m.register("actor/1/on", test_name)
    m.register("actor/1/on", test_name)
    m.register("actor/1/on", test_name)

    print(m.get_callbacks("actor/1/on"))


    m.unregister("actor/1/on")

    for methods in  m.iter_match("actor/1/on"):

        for f in methods:
            f()

