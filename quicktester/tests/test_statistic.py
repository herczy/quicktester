import json
import datetime
import time
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

    def test_get_failing_ids(self):
        self.assertSetEqual({1, 2}, Report.get_failing_ids())

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
        for report in self.reports:
            res.report_run(report)

        return res

    def assert_failures(self, expected, backlog=1):
        self.assertSetEqual(
            set(expected),
            self.initialize_statistic().get_failure_paths(backlog)
        )

    def add_report(self, *statuses):
        res = Report()
        for case, status in statuses:
            res.add(case, status)

        self.reports.append(res)

    def setUp(self):
        self.test = FakeTest('/path/a/b', 'a.b', 'Test.func')
        self.reports = []
        self.add_report(
            (self.test, Report.STATUS_PASSED)
        )

    def test_check_if_nothing_failed(self):
        statistic = self.initialize_statistic()

        self.assertFalse(statistic.check_if_failed(self.test, 1))

    def test_check_if_recent_failed(self):
        self.add_report(
            (self.test, Report.STATUS_ERROR)
        )
        statistic = self.initialize_statistic()

        self.assertTrue(statistic.check_if_failed(self.test, 1))

    def test_check_if_nonrecent_failed(self):
        self.add_report(
            (self.test, Report.STATUS_ERROR)
        )
        self.add_report()
        statistic = self.initialize_statistic()

        self.assertFalse(statistic.check_if_failed(self.test, 1))
        self.assertTrue(statistic.check_if_failed(self.test, 2))

    def test_check_if_module_failed(self):
        module_failure = FakeTest('/path/a/b', 'a.b', None)
        self.add_report(
            (module_failure, Report.STATUS_ERROR)
        )

        statistic = self.initialize_statistic()

        self.assertTrue(statistic.check_if_failed(module_failure, 1))
        self.assertTrue(statistic.check_if_failed(self.test, 1))
        self.assertFalse(statistic.check_if_failed(FakeTest('/a/c', 'a.c', None), 1))
        self.assertFalse(statistic.check_if_failed(FakeTest('/a/c', 'a.c', 'd.e'), 1))

    def test_report_all_passing(self):
        self.assert_failures([])

    def test_backlog_must_be_bigger_than_zero(self):
        stat = self.initialize_statistic()

        self.assertRaises(ValueError, stat.get_failure_paths, 0)
        self.assertRaises(ValueError, stat.dump_info, 0)
        self.assertRaises(ValueError, stat.check_if_failed, FakeTest('', '', ''), 0)

    def test_report_with_failure(self):
        self.add_report(
            (self.test, Report.STATUS_FAILED)
        )

        self.assert_failures(['/path/a/b'])

    def test_report_with_errors(self):
        self.add_report(
            (self.test, Report.STATUS_ERROR)
        )


        self.assert_failures(['/path/a/b'])

    def test_report_multiple_runs(self):
        self.add_report(
            (self.test, Report.STATUS_ERROR)
        )
        self.add_report(
            (self.test, Report.STATUS_PASSED)
        )

        self.assert_failures([])
        self.assert_failures(['/path/a/b'], backlog=2)

    def __prepare_statistics(self, new_test_base_path='/path/'):
        new_test = FakeTest(new_test_base_path + 'a/b', 'a.b', 'Test.func2')
        passing_test = FakeTest('/path/a/b', 'a.b', 'Test.passing')

        self.add_report(
            (new_test, Report.STATUS_PASSED),
            (passing_test, Report.STATUS_PASSED)
        )
        self.add_report(
            (self.test, Report.STATUS_PASSED),
            (passing_test, Report.STATUS_PASSED)
        )
        self.add_report(
            (self.test, Report.STATUS_FAILED),
            (new_test, Report.STATUS_SKIPPED),
            (passing_test, Report.STATUS_PASSED)
        )
        self.add_report(
            (self.test, Report.STATUS_ERROR),
            (new_test, Report.STATUS_PASSED),
            (passing_test, Report.STATUS_PASSED)
        )

        return self.initialize_statistic()

    def __dump_info(self, backlog=10, relpath='/path/', new_test_base_path=None, **kwargs):
        f = StringIO()
        if new_test_base_path is None:
            new_test_base_path = relpath

        kwargs['file'] = f
        self.__prepare_statistics(new_test_base_path).dump_info(backlog, relpath, **kwargs)

        return f.getvalue().strip()

    def assertDumped(self, expected, *args, **kwargs):
        self.assertEqual(expected.strip(), self.__dump_info(*args, **kwargs))

    def test_dump_info(self):
        self.assertDumped(
            '''\
[     . .FE] a/b:a.b:Test.func
[      . S.] a/b:a.b:Test.func2
[      ....] a/b:a.b:Test.passing

3 test(s) out of 3 shown
            '''
        )

    def test_dump_info_relative_to_a_path(self):
        self.assertDumped(
            '''\
[     . .FE] a/b:a.b:Test.func
[      ....] a/b:a.b:Test.passing

2 test(s) out of 3 shown
            ''',
            new_test_base_path='/otherpath/'
        )

    def test_dump_all_info(self):
        self.assertDumped(
            '''\
[      . S.] ../otherpath/a/b:a.b:Test.func2
[     . .FE] a/b:a.b:Test.func
[      ....] a/b:a.b:Test.passing

3 test(s) out of 3 shown
            ''',
            new_test_base_path='/otherpath/',
            dump_all=True
        )

    def test_dump_failonly_info(self):
        self.assertDumped(
            '''\
[     . .FE] a/b:a.b:Test.func

1 test(s) out of 3 shown
            ''',
            failonly=True
        )

    def test_dump_json_info(self):
        info = self.__dump_info(1, format_json=True, failonly=True)

        self.assertEqual(
            {
                "runs": [
                    [
                        {
                            "path": "a/b",
                            "module": "a.b",
                            "call": "Test.func",
                            "runtime": time.strftime("%Y-%m-%d %H:%M +0000", time.gmtime(0)),
                            "status": "error",
                        }
                    ]
                ],
                "summary": {"total": 3, "shown": 1}
            },
            json.loads(info)
        )


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

    def report_run(self, run):
        self.__runs.append([(case.address(), status.id) for case, status in run])

    def get_last_runid(self):
        return max(0, len(self.__runs) - 1)

    def get_failure_set(self, backlog):
        res = set()
        for run in self.__runs[- backlog:]:
            for case, status in run:
                if Report.get_status_by_id(status).failing:
                    res.add(case)

        return res

    EPOCH = datetime.datetime(1970, 1, 1)
    def get_run(self, runid):
        for (path, module, call), status in self.__runs[runid]:
            yield path, module, call, Report.get_status_by_id(status), self.EPOCH

    def get_test_count(self):
        tests = set()
        for run in self.__runs:
            tests.update(addr for addr, _ in run)

        return len(tests)


class FakeDatabaseFactory(object):
    def __init__(self):
        self.database = FakeDatabase()

    def init_connection(self, filename):
        return self.database
