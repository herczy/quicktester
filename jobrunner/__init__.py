from __future__ import print_function

import imp
import sys
import os.path
import subprocess
import argparse
import unittest
import nose.loader
import collections


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


class ModuleDiscovery(object):
    def __init__(self):
        self.__packages = []

    @property
    def packages(self):
        return iter(self.__packages)

    def discover_all(self, path):
        try:
            self.add_module_path(path)
            return

        except RuntimeError:
            pass

        if os.path.isdir(path):
            for sub in os.listdir(path):
                full = os.path.join(path, sub)

                try:
                    self.add_module_path(full)

                except RuntimeError:
                    pass

    def add_module_path(self, path):
        module = self.__get_module(path)
        if module is None:
            raise RuntimeError('{} is not a module nor a package'.format(path))

        self.__packages.append(module)

    def find_related_package(self, path, packages=None):
        if path.endswith('__init__.py'):
            path = os.path.dirname(path)

        path = os.path.abspath(path)
        if packages is None:
            packages = self.__packages

        for module in packages:
            if module.path == path:
                return module

            elif path.startswith(module.path):
                return self.find_related_package(path, packages=module.children)

        raise RuntimeError('Cannot find related package for {}'.format(path))

    @classmethod
    def __get_module(cls, path):
        if os.path.isfile(path):
            return Module.from_filename(path)

        elif os.path.isfile(os.path.join(path, '__init__.py')):
            pkg = Package.from_filename(path)

            for sub in os.listdir(path):
                if sub in {'__init__.py', '__init__.pyc'}:
                    continue

                full = os.path.join(path, sub)

                module = cls.__get_module(full)
                if module is not None:
                    pkg.add_child(module)

            return pkg


class GitChanges(object):
    def __init__(self):
        self.__changed = []
        self.__collect_changes()

    @property
    def changes(self):
        return iter(self.__changed)

    def __collect_changes(self):
        try:
            res = subprocess.check_output(['git', 'status', '--porcelain']).decode()

        except subprocess.CalledProcessError:
            return

        for line in res.split('\n'):
            index, filename = line[:2], line[3:]
            self.__changed.append(filename)

    @classmethod
    def list_changed_packages(cls, discovery):
        for filename in cls().changes:
            try:
                yield filename, discovery.find_related_package(filename)

            except RuntimeError:
                continue


class TestRunner(object):
    def __init__(self, packages):
        self.__cases = []
        self.__get_cases(packages, nose.loader.TestLoader())

    def __get_cases(self, packages, loader):
        scanned = set()
        for module in packages:
            if isinstance(module, Package):
                load_from = module

            else:
                load_from = module.parent

            if load_from is None:
                continue

            if load_from.fqdn in scanned:
                continue

            self.__cases.extend(load_from.load_related_tests(loader))
            scanned.add(load_from.fqdn)

    def run(self):
        result = unittest.TestResult()

        for case in self.__cases:
            case.run(result)

        self.__print_result(result)
        if not result.wasSuccessful():
            return 1

    def __print_result(self, result):
        self.__print_traces('ERROR', result.errors)
        self.__print_traces('FAIL', result.failures)

    def __print_traces(self, status, reslist):
        for test, trace in reslist:
            self.__print_failure(status, test, trace)

    def __print_failure(self, status, test, trace):
        print('=' * 70)
        print('{}: {}'.format(status, test))
        print('-' * 70)
        print(trace)
