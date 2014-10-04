import os.path
import unittest

from . import FakeConfig

from .. import util


class TestUtil(unittest.TestCase):
    def test_is_reldir(self):
        self.assertTrue(util.is_reldir('a/b', ''))
        self.assertTrue(util.is_reldir('a/b', 'a'))
        self.assertFalse(util.is_reldir('a/b', 'b'))

    def test_is_in_restricted(self):
        self.assertFalse(util.is_in_restricted('something', []))
        self.assertTrue(util.is_in_restricted('a/b', ['a']))
        self.assertTrue(util.is_in_restricted('a/b', ['a', 'b']))
        self.assertFalse(util.is_in_restricted('c', ['a']))

    def test_restrict(self):
        self.assertListEqual(
            ['a/b', 'a/c', 'b/a', 'a', 'b'],
            util.restrict(
                ['a/b', 'c', 'a/c', 'b/a', 'c/b', 'a', 'b', 'c'],
                ['a', 'b']
            )
        )

    DIRECTORIES = {'package', 'tests'}

    def __isdir(self, path):
        return os.path.basename(path) in self.DIRECTORIES

    def test_get_testing_paths(self):
        self.assertListEqual(
            [
                'package/tests/test_something.py',
                'package',
                'package/tests',
            ],
            util.get_testing_paths(
                [
                    'package/tests/test_something.py',
                    'package/module.py',
                    'package/tests',
                ],
                os_isdir_func=self.__isdir
            )
        )

    def test_reduce_paths(self):
        self.assertListEqual([], util.reduce_paths([]))
        self.assertListEqual(['singlepath'], util.reduce_paths(['singlepath']))
        self.assertListEqual(
            ['path0'],
            util.reduce_paths(['path0', 'path0/path1'])
        )
        self.assertListEqual(
            ['path0'],
            util.reduce_paths(['path0/path1', 'path0'])
        )

    def __assert_testname_reduction(self, expected, names, relevant):
        config = FakeConfig(names)
        util.update_test_names(config, relevant)

        self.assertListEqual(expected, config.testNames)

    def test_update_test_names(self):
        self.__assert_testname_reduction(['a', 'b'], [], ['a', 'b'])
        self.__assert_testname_reduction(['a/b'], ['a/b'], ['a'])
        self.__assert_testname_reduction(['a'], ['a', 'a/b'], ['a'])
        self.__assert_testname_reduction(['a', 'c'], ['a', 'c'], ['a/b'])
