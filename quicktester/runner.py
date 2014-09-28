import unittest
import nose

from .module import Package
from .statistic import Statistic


class RunnerConfig(object):
    def __init__(
            self,
            verbosity=1,
            stop_on_error=False,
            statfile='./.quicktest-runstat'
    ):
        self.__statistics = Statistic(statfile)
        self.__config = nose.config.Config(
            env={
                'NOSE_VERBOSITY': verbosity,
                'NOSE_STOP': stop_on_error,
            }
        )
        self.__loader = nose.loader.TestLoader(config=self.__config)
        self.__runner = nose.core.TextTestRunner(config=self.__config)
        self.__suite_factory = nose.suite.ContextSuiteFactory(config=self.__config)

    @property
    def loader(self):
        return self.__loader

    @property
    def runner(self):
        return self.__runner

    @property
    def statistics(self):
        return self.__statistics

    @property
    def suite_factory(self):
        return self.__suite_factory


class TestRunner(object):
    def __init__(self, packages, config=None):
        if config is None:
            config = RunnerConfig()

        self.__config = config
        self.__cases = self.__get_cases(packages, self.__config.loader)

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

        failures, rest = self.__config.statistics.order_by_failure(res)
        return failures + rest

    def run(self):
        result = self.__config.runner.run(self.__config.suite_factory(self.__cases))
        self.__config.statistics.report_result(result)

        if not result.wasSuccessful():
            return 1
