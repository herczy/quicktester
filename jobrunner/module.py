import os.path


class Module(object):
    def __init__(self, name, path):
        self.__name = name
        self.__path = os.path.abspath(path)
        self.__parent = None

    @property
    def name(self):
        return self.__name

    @property
    def path(self):
        return self.__path

    @property
    def parent(self):
        return self.__parent

    @property
    def fqdn(self):
        if self.__parent is None:
            return self.__name

        return self.__parent.fqdn + '.' + self.__name

    @property
    def children(self):
        return ()

    @parent.setter
    def parent(self, value):
        assert self.__parent is None
        assert isinstance(value, Module)

        self.__parent = value

    @property
    def root(self):
        if self.__parent is None:
            return self

        return self.__parent.root

    @property
    def is_test_module(self):
        return self.__name.startswith('test_')

    @classmethod
    def from_filename(cls, path):
        name, ext = os.path.splitext(os.path.basename(path))

        if ext != '.py':
            return None

        return cls(name, path)

    def load_related_tests(self, loader):
        return ()


class Package(Module):
    def __init__(self, *args, **kwargs):
        super(Package, self).__init__(*args, **kwargs)

        self.__children = []

    @property
    def children(self):
        return tuple(self.__children)

    def add_child(self, child):
        child.parent = self
        self.__children.append(child)

    @classmethod
    def from_filename(cls, path):
        return cls(os.path.basename(path), path)

    def __flatten(self, suite):
        if isinstance(suite, collections.Iterable):
            res = []
            for item in suite:
                res.extend(self.__flatten(item))

            return res

        return [suite]

    def load_related_tests(self, loader):
        res = []
        for suite in loader.loadTestsFromDir(self.path):
            res.extend(self.__flatten(suite))

        return res
