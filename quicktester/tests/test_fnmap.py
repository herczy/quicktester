import unittest

from ..fnmap import RegexMapping, DefaultMapping, builtin_mappings


class TestRegexMapping(unittest.TestCase):
    def setUp(self):
        self.mapping = RegexMapping(
            [
                (r'(.*/test_.*\.py)', r'\1'),
                (r'(.*)/.*\.py', r'\1'),
            ]
        )

    def test_map(self):
        self.assertEqual('/path/to', self.mapping.map('/path/to/module.py'))

    def test_map_maps_to_same_file(self):
        self.assertEqual('/path/to/nonpython', self.mapping.map('/path/to/nonpython'))

    def test_precedence_is_kept(self):
        path = '/path/to/package/tests/test_something.py'

        self.assertEqual(path, self.mapping.map(path))

    def test_replace_variables_in_source(self):
        workdir = '/path/to/workdir'
        path = workdir + '/test.py'
        altmapping = RegexMapping([(r'@WORKDIR@/(.*\.py)', r'\1'),])

        self.assertEqual(path, altmapping.map(path, {'WORKDIR': '/somedir'}))
        self.assertEqual('test.py', altmapping.map(path, {'WORKDIR': workdir}))

    def test_replace_variables_in_target(self):
        altmapping = RegexMapping([(r'.*\.py', r'@WORKDIR@'),])

        self.assertEqual('workdir', altmapping.map('test_something.py', {'WORKDIR': 'workdir'}))

    def test_normalize_argument_paths(self):
        self.assertEqual('/path/to', self.mapping.map('///path/./to/some/../module.py'))

    def test_normalize_result_paths(self):
        self.assertEqual(
            '/path/to/module.py',
            RegexMapping([(r'(.*)', r'///path/./to/some/../module.py')]).map('')
        )


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


class TestBuiltinMappings(unittest.TestCase):
    def test_match_mapping(self):
        mapping = builtin_mappings['match']
        path = '/path/to/package/tests/test_something.py'

        self.assertEqual('/path/to/tests/test_module.py', mapping.map('/path/to/module.py'))
        self.assertEqual('/path/to/nonpython', mapping.map('/path/to/nonpython'))
        self.assertEqual(path, mapping.map(path))

    def test_external_mapping(self):
        mapping = builtin_mappings['external']
        variables = {'BASEPATH': '/path/to/project', 'TESTDIR': 'tests'}

        self.assertEqual(
            '/path/to/project/tests/test_module.py',
            mapping.map('/path/to/project/package/module.py', variables)
        )
        self.assertEqual(
            '/path/to/project/tests/subpackage/test_module.py',
            mapping.map('/path/to/project/package/subpackage/module.py', variables)
        )
        self.assertEqual('/path/to/nonpython', mapping.map('/path/to/nonpython', variables))
        self.assertEqual(
            '/path/to/project/tests/test_something.py',
            mapping.map('/path/to/project/tests/test_something.py', variables)
        )
