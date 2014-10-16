import unittest

from ..fnmap import DefaultMapping, NameMatchMapping, ExternalNameMapping


class TestDefaultMapping(unittest.TestCase):
    def setUp(self):
        self.mapping = DefaultMapping()

    def test_nonpython_file(self):
        self.assertEqual('/path/to/nonpython', self.mapping.map('/path/to/nonpython'))

    def test_python_module(self):
        self.assertEqual('/path/to', self.mapping.map('/path/to/module.py'))

    def test_python_test_module(self):
        path = '/path/to/package/tests/test_something.py'

        self.assertEqual(path, self.mapping.map(path))


class TestNameMatchMapping(unittest.TestCase):
    def setUp(self):
        self.mapping = NameMatchMapping()

    def test_nonpython_file(self):
        self.assertEqual('/path/to/nonpython', self.mapping.map('/path/to/nonpython'))

    def test_python_module(self):
        self.assertEqual('/path/to/tests/test_module.py', self.mapping.map('/path/to/module.py'))

    def test_python_test_module(self):
        path = '/path/to/package/tests/test_something.py'

        self.assertEqual(path, self.mapping.map(path))


class TestExternalNameMapping(unittest.TestCase):
    def setUp(self):
        self.mapping = ExternalNameMapping()
        self.variables = {'BASEPATH': '/path/to/project', 'TESTDIR': 'tests'}

    def test_nonpython_file(self):
        self.assertEqual(
            '/path/to/nonpython',
            self.mapping.map('/path/to/nonpython', self.variables)
        )

    def test_python_module(self):
        self.assertEqual(
            '/path/to/project/tests/test_module.py',
            self.mapping.map('/path/to/project/package/module.py', self.variables)
        )

    def test_python_module_in_subpackage(self):
        self.assertEqual(
            '/path/to/project/tests/subpackage/test_module.py',
            self.mapping.map('/path/to/project/package/subpackage/module.py', self.variables)
        )

    def test_python_test_module(self):
        self.assertEqual(
            '/path/to/project/tests/test_something.py',
            self.mapping.map('/path/to/project/tests/test_something.py', self.variables)
        )
