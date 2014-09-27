import unittest
import nose

from .module import Package
from .statistic import Statistic


class TestRunner(object):
    def __init__(self, packages, statfile='./.quicktest-runstat'):
        self.__statistics = Statistic(statfile)
        self.__cases = self.__get_cases(packages, nose.loader.TestLoader())

    def __get_cases(self, packages, loader):
        cases = []
        res = []
        repeat = set()

        for module in packages:
            if isinstance(module, Package):
                load_from = module

            else:
                load_from = module.parent

            if load_from is None:
                continue

            for case in load_from.load_related_tests(loader):
                addr = nose.util.test_address(case)

                if addr in repeat:
                    continue

                res.append(case)
                repeat.add(addr)

        failures, rest = self.__statistics.order_by_failure(res)
        return failures + rest

    def run(self, verbosity):
        runner = nose.core.TextTestRunner(verbosity=verbosity)
        result = runner.run(unittest.TestSuite(self.__cases))
        self.__statistics.report_result(result)

        if not result.wasSuccessful():
            return 1
