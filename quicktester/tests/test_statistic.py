import tempfile
import unittest
import os.path
import shutil
import io
import sys

from ..statistic import Report, Statistic, DatabaseFactory


if sys.version_info.major >= 3:
    StringIO = io.StringIO

else:
    StringIO = io.BytesIO


class TestReport(unittest.TestCase):
    def setUp(self):
        self.report = Report()
        self.report.add(
            FakeTest('/path/to/test', 'test', 'TestSuite.test_case'),
            Report.STATUS_PASSED
        )
        self.report.add(
            FakeTest('/path/to/test', 'test', 'TestSuite.test_failing_case'),
            Report.STATUS_FAILED
        )

    def test_get_status_by_id(self):
        self.assertRaises(KeyError, Report.get_status_by_id, -1)
        self.assertEqual(Report.STATUS_PASSED, Report.get_status_by_id(0))
        self.assertEqual(Report.STATUS_FAILED, Report.get_status_by_id(1))
        self.assertEqual(Report.STATUS_ERROR, Report.get_status_by_id(2))
        self.assertEqual(Report.STATUS_SKIPPED, Report.get_status_by_id(3))
        self.assertRaises(KeyError, Report.get_status_by_id, 4)

    def test_get_entries(self):
        self.assertListEqual(
            [
                ('TestSuite.test_case', Report.STATUS_PASSED),
                ('TestSuite.test_failing_case', Report.STATUS_FAILED),
            ],
            [(case.address()[-1], status) for case, status in self.report]
        )


class TestStatistics(unittest.TestCase):
    def initialize_statistic(self):
        res = Statistic(None, dbfactory=FakeDatabaseFactory())
        for result in self.results:
            res.report_result(result)

        return res

    def assert_failures(self, expected, backlog=1):
        self.assertSetEqual(
            set(expected),
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
        stat = self.initialize_statistic()

        self.assertRaises(ValueError, stat.get_failure_paths, 0)
        self.assertRaises(ValueError, stat.dump_info, 0)
        self.assertRaises(ValueError, stat.check_if_failed, FakeTest('', '', ''), 0)

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

    EXPECTED_OUTPUT = '''\
[       .FF] a/b:a.b:Test.func
[       .F.] a/b:a.b:Test.func2
'''

    def test_dump_info(self):
        statistic = self.initialize_statistic()
        self.tests += (FakeTest('/path/a/b', 'a.b', 'Test.func2'),)
        self.results[0].tests.append(self.tests[-1])

        statistic.report_result(self.results[0])

        self.results[0].errors.append((self.tests[0], ''))
        self.results[0].errors.append((self.tests[1], ''))
        statistic.report_result(self.results[0])

        self.results[0].errors = []
        self.results[0].failures.append((self.tests[0], ''))
        statistic.report_result(self.results[0])

        f = StringIO()
        statistic.dump_info(10, relto='/path/', file=f)

        self.assertEqual(self.EXPECTED_OUTPUT, f.getvalue())


class TestDatabaseFactory(unittest.TestCase):
    # NOTE: DatabaseFactory is not directly tested, but rather through the
    # Statistic class which uses DatabaseFactory by default. To still reflect
    # this, we use the 'dbfactory' argument directly.

    def initialize_statistic(self, filename):
        return Statistic(filename, dbfactory=DatabaseFactory())

    def test_can_load_if_file_does_not_exist(self):
        with TemporaryStatisticsFile() as filename:
            self.assertSetEqual(set(), self.initialize_statistic(filename).get_failure_paths(1))

    def test_load_legacy_format_with_no_failures_as_the_first_run(self):
        with tempfile.NamedTemporaryFile(prefix='quicktester.', mode='w') as f:
            f.write('[[], [["a/b", "a.b", "TestCase.test_func"]]]')
            f.flush()

            self.assertSetEqual({'a/b'}, self.initialize_statistic(f.name).get_failure_paths(2))

    def test_load_legacy_format_with_a_failure_in_the_first_run(self):
        with tempfile.NamedTemporaryFile(prefix='quicktester.', mode='w') as f:
            f.write('[[["a/b", "a.b", "TestCase.test_func"]]]')
            f.flush()

            self.assertSetEqual({'a/b'}, self.initialize_statistic(f.name).get_failure_paths(1))


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


class TemporaryStatisticsFile(object):
    def __enter__(self):
        self.__tempdir = tempfile.mkdtemp(prefix='quicktester.')
        return os.path.join(self.__tempdir, 'db')

    def __exit__(self, *args):
        shutil.rmtree(self.__tempdir, ignore_errors=True)


class FakeDatabase(object):
    def __init__(self):
        self.__runs = []

    def report_run(self, cases):
        self.__runs.append([case.address() for case, _ in cases])

    def get_last_runid(self):
        return max(0, len(self.__runs) - 1)

    def get_failure_set(self, backlog):
        return set(case for run in self.__runs[- backlog:] for case in run)

    def get_runs(self, backlog):
        for runid in range(len(self.__runs) - backlog, len(self.__runs)):
            if runid < 0:
                continue

            for path, module, call in self.__runs[runid]:
                yield path, module, call, self.get_last_runid() - runid


class FakeDatabaseFactory(object):
    def __init__(self):
        self.database = FakeDatabase()

    def init_connection(self, filename):
        return self.database
