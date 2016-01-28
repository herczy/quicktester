import os.path
import unittest

from . import FakeConfig

from ..util import is_reldir


class TestUtil(unittest.TestCase):
    def test_is_reldir(self):
        self.assertTrue(is_reldir('a/b', ''))
        self.assertTrue(is_reldir('a/b', 'a'))
        self.assertFalse(is_reldir('a/b', 'b'))
