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


class TestChangesIntegration(clone.RepoTestCase):
    integration = True
    # NOTE: Move into a features file or something

    def test_unchanged_repository(self):
        self.assertEqual(set(), set(Changes()))

    def test_not_a_git_repo(self):
        shutil.rmtree(self.clone.get_path('.git'), ignore_errors=True)

        self.assertRaises(GitError, Changes)
