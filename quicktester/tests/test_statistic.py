import tempfile
import unittest
import json

from ..statistic import Statistic


class TestStatistics(unittest.TestCase):
    def initialize_statistic(self):
        statistic = Statistic(None)

        for result in self.results:
            statistic.report_result(result)

        return statistic

    def assert_failures(self, expected, backlog=1):
        self.assertListEqual(
            expected,
            self.initialize_statistic().get_failure_paths(backlog)
        )

    def setUp(self):
        self.tests = (
            FakeTest('/path/a/b', 'a.b', 'Test.func'),
        )
        self.results = [
            FakeResult(self.tests),
        ]

    def test_check_if_nothing_failed(self):
        statistic = self.initialize_statistic()

        self.assertFalse(statistic.check_if_failed(self.tests[0], 1))

    def test_check_if_recent_failed(self):
        self.results[0].errors.append((self.tests[0], None))
        statistic = self.initialize_statistic()

        self.assertTrue(statistic.check_if_failed(self.tests[0], 1))

    def test_check_if_nonrecent_failed(self):
        self.results[0].errors.append((self.tests[0], None))
        self.results.append(FakeResult(self.tests))
        statistic = self.initialize_statistic()

        self.assertFalse(statistic.check_if_failed(self.tests[0], 1))
        self.assertTrue(statistic.check_if_failed(self.tests[0], 2))

    def test_report_all_passing(self):
        self.assert_failures([])

    def test_backlog_must_be_bigger_than_zero(self):
        self.assertRaises(ValueError, Statistic(None).get_failure_paths, 0)
        self.assertRaises(ValueError, Statistic(None).dump_info, 0)
        self.assertRaises(ValueError, Statistic(None).check_if_failed, object(), 0)

    def test_report_with_failure(self):
        self.results[0].failures.append((self.tests[0], None))

        self.assert_failures(['/path/a/b'])

    def test_report_with_errors(self):
        self.results[0].errors.append((self.tests[0], None))

        self.assert_failures(['/path/a/b'])

    def test_report_multiple_runs(self):
        self.results[0].errors.append((self.tests[0], None))
        self.results.append(FakeResult(self.tests))

        self.assert_failures([])
        self.assert_failures(['/path/a/b'], backlog=2)

    def test_persistence(self):
        with tempfile.NamedTemporaryFile(mode='w') as f:
            f.write('[]')
            f.flush()

            self.results[0].errors.append((self.tests[0], ''))
            Statistic(f.name).report_result(self.results[0])

            statistic = Statistic(f.name)
            self.assertListEqual(['/path/a/b'], statistic.get_failure_paths(1))

    EXPECTED_OUTPUT = '''\
[       .FF] a/b:a.b:Test.func
[       .F.] a/b:a.b:Test.func2
'''

    def test_dump_info(self):
        statistic = Statistic(None)
        self.tests += (FakeTest('/path/a/b', 'a.b', 'Test.func2'),)
        self.results[0].tests.append(self.tests[-1])

        statistic.report_result(self.results[0])

        self.results[0].errors.append((self.tests[0], ''))
        self.results[0].errors.append((self.tests[1], ''))
        statistic.report_result(self.results[0])

        self.results[0].errors = []
        self.results[0].failures.append((self.tests[0], ''))
        statistic.report_result(self.results[0])

        with tempfile.NamedTemporaryFile(mode='w+') as f:
            statistic.dump_info(10, relto='/path/', file=f)
            f.flush()
            f.seek(0)

            self.assertEqual(self.EXPECTED_OUTPUT, f.read())

    def test_can_load_if_file_does_not_exist(self):
        statistic = Statistic('/path/to/nonexistent/file')

        self.assertListEqual([], statistic.get_failure_paths(1))


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
