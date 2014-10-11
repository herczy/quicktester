import unittest
import tempfile
import os.path

from ..cache import Cache, Loader, ExpiredError

from . import StringIO


class TestCache(unittest.TestCase):
    def setUp(self):
        self.loaded = False
        self.obj = object()

        self.cache = Cache()
        self.cache(ExampleLoader(content='empty', time=10))

    def test_load_expired(self):
        loader = ExampleLoader()

        self.assertEqual('hello, world', self.cache(loader))
        self.assertTrue(loader.loaded)

        loader.content += '!'
        self.assertEqual('hello, world', self.cache(loader))

    def test_load_already_loaded(self):
        loader = ExampleLoader()
        loader.time = 5

        self.assertEqual('empty', self.cache(loader))
        self.assertFalse(loader.loaded)

    def test_persistence(self):
        dest = StringIO()
        self.cache.save(dest)

        cache = Cache()
        cache.load(StringIO(dest.getvalue()))

        self.assertEqual('empty', cache(ExampleLoader(time=0)))


class ExampleLoader(Loader):
    loaded = False
    ident = 0
    time = 15
    content = 'hello, world'

    def __init__(self, **kwargs):
        for attr, value in kwargs.items():
            setattr(self, attr, value)

    def get_ident(self):
        return self.ident

    def get_time(self):
        return self.time

    def __call__(self):
        self.loaded = True
        return self.content
