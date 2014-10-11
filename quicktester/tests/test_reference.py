import unittest

import os.path
import ast

from ..reference import References


class TestReferences(unittest.TestCase):
    def setUp(self):
        self.importer = FakeImporter()

    def make_references(self, script, filename):
        return References(
            ast.parse(script),
            filename=filename,
            cwd=self.importer.cwd,
            _import=self.importer
        )

    def assert_properly_processed(
            self,
            expected,
            script,
            filename='package/subpackage/something.py'
    ):
        refs = self.make_references(script, filename)

        self.assertSetEqual(set(expected), set(refs))

    def test_no_references(self):
        self.assert_properly_processed(
            [],
            'print("hello, world")',
            'package/module.py'
        )

    def test_references_package_relative(self):
        self.assert_properly_processed(
            ['package/module.py'],
            'from .. import module'
        )

    def test_references_package_absolute(self):
        self.assert_properly_processed(
            ['package/module.py'],
            'import package.module'
        )

    def test_references_package_external(self):
        self.assert_properly_processed(
            [],
            'import urllib.parse'
        )

    def test_import_error(self):
        self.importer.raise_import_error = True
        self.assert_properly_processed(
            [],
            'import package.subpackage'
        )

    def test_import_complex_example(self):
        self.assert_properly_processed(
            ['package/subpackage/submodule.py', 'package/subpackage/submodule2.py'],
            'from ...package.subpackage import submodule, submodule2 as m'
        )


class FakeImporter(object):
    root_packages = {
        'package': 'package/',
        'other': 'other/',
    }

    cwd = '/path/to/cwd'
    raise_import_error = False

    def __call__(self, name):
        if self.raise_import_error:
            raise ImportError(name)

        full = name.split('.')
        path = '/'.join(full) + '.py'

        if full[0] not in self.root_packages:
            return FakeModule(os.path.abspath(os.path.join('/usr/lib/python/{}'.format(path))))

        return FakeModule(os.path.join(self.cwd, path))


class FakeModule(object):
    __file__ = None

    def __init__(self, path):
        self.__file__ = path
