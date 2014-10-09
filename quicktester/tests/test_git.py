import unittest
import shutil

from . import clone

from ..git import Changes, GitError


class TestChanges(unittest.TestCase):
    def __git_status_func(self, result):
        def __status():
            return result

        return __status

    def test_initialize(self):
        changes = Changes(git_status_func=self.__git_status_func('?? a\n M b\n'))
        self.assertEqual(2, len(changes))
        self.assertIn('a', changes)
        self.assertNotIn('c', changes)
        self.assertSetEqual({'a', 'b'}, set(changes))
