import tempfile
import unittest
import json

from ..statistic import Statistic


class TestStatistics(unittest.TestCase):
    def assert_failures(self, expected, backlog=1):
        statistic = Statistic(None)

        for result in self.results:
            statistic.report_result(result)
        
        self.assertListEqual(
            expected,
            statistic.get_failure_paths(backlog)
        )

    def setUp(self):
        self.tests = (
            FakeTest('/path/a/b', 'a.b', 'Test.func'),
        )
        self.results = [
            FakeResult(self.tests),
        ]

    def test_report_all_passing(self):
        self.assert_failures([])

    def test_backlog_must_be_bigger_than_zero(self):
        self.assertRaises(ValueError, Statistic(None).get_failure_paths, 0)
        self.assertRaises(ValueError, Statistic(None).dump_info, 0)

    def test_report_with_failure(self):
        self.results[0].failures.append(self.tests[0])

        self.assert_failures(['/path/a/b'])

    def test_report_with_errors(self):
        self.results[0].errors.append(self.tests[0])

        self.assert_failures(['/path/a/b'])

    def test_report_multiple_runs(self):
        self.results[0].errors.append(self.tests[0])
        self.results.append(FakeResult(self.tests))

        self.assert_failures([])
        self.assert_failures(['/path/a/b'], backlog=2)

    def test_persistence(self):
        with tempfile.NamedTemporaryFile(mode='w') as f:
            f.write('[]')
            f.flush()

            self.results[0].errors.append(self.tests[0])
            Statistic(f.name).report_result(self.results[0])

            statistic = Statistic(f.name)
            self.assertListEqual(['/path/a/b'], statistic.get_failure_paths(1))

    EXPECTED_OUTPUT = '''\
[       .FF] /path/a/b:a.b:Test.func
'''

    def test_dump_info(self):
        statistic = Statistic(None)

        statistic.report_result(self.results[0])

        self.results[0].errors.append(self.tests[0])
        statistic.report_result(self.results[0])

        self.results[0].errors = []
        self.results[0].failures.append(self.tests[0])
        statistic.report_result(self.results[0])

        with tempfile.NamedTemporaryFile(mode='w+') as f:
            statistic.dump_info(10, file=f)
            f.flush()
            f.seek(0)

            self.assertEqual(self.EXPECTED_OUTPUT, f.read())


class FakeResult(object):
    def __init__(self, tests):
        self.tests = list(tests)
        self.failures = []
        self.errors = []


class FakeTest(object):
    def __init__(self, path, module, call):
        self.__address = (path, module, call)

    def address(self):
        return self.__address
