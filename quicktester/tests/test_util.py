import os.path
import unittest

from . import FakeConfig

from .. import util


class TestUtil(unittest.TestCase):
    def test_is_reldir(self):
        self.assertTrue(util.is_reldir('a/b', ''))
        self.assertTrue(util.is_reldir('a/b', 'a'))
        self.assertFalse(util.is_reldir('a/b', 'b'))
