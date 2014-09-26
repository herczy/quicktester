from __future__ import print_function

import unittest
import nose.loader

from .module import Package


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
