from __future__ import print_function

import sys
import os.path
import json
import nose
import datetime

import sqlite3


DEFAULT_STATISTICS_FILE = '.quicktester-statistics'


TABLE_DEF_TESTS = '''
    CREATE TABLE tests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT,
        module TEXT,
        call TEXT
    );
'''

TABLE_DEF_RUN = '''
    CREATE TABLE runs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        runtime DATETIME
    );
'''

TABLE_DEF_FAILURES = '''
    CREATE TABLE failures (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        testid INTEGER REFERENCES tests (id),
        runid INTEGER REFERENCES runs (id),
        failtime DATETIME
    );
'''


class Statistic(object):
    def __init__(self, filename):
        self.__filename = filename

        self.__exists = os.path.isfile(self.__filename)
        self.__sqlite = sqlite3.connect(self.__filename)
        if not self.__exists:
            self.__create_table()

        self.__failed_tests = None

    @property
    def existed(self):
        return self.__exists

    def report_result(self, result):
        try:
            runid = self.__get_new_runid()

            for case, _ in result.errors:
                self.__report_failure(case, runid)

            for case, _ in result.failures:
                self.__report_failure(case, runid)

        except:
            self.__sqlite.rollback()

        self.__sqlite.commit()

    def check_if_failed(self, case, max_runid):
        if self.__failed_tests is None:
            self.__load_failures()

        if not self.existed:
            return True

        failid = self.__failed_tests.get(nose.util.test_address(case), None)
        return self.__check_failid(failid, max_runid)

    def get_failure_paths(self, max_runid):
        if self.__failed_tests is None:
            self.__load_failures()

        res = set()
        for key, failid in self.__failed_tests.items():
            path, module, call = key
            if not self.__check_failid(failid, max_runid):
                continue

            res.add(path)

        return res

    def __check_failid(self, failid, max_runid):
        return failid is not None and failid >= 1 - max_runid

    def __create_table(self):
        self.__sqlite.execute(TABLE_DEF_TESTS)
        self.__sqlite.execute(TABLE_DEF_FAILURES)
        self.__sqlite.execute(TABLE_DEF_RUN)
        self.__sqlite.commit()

    def __report_failure(self, case, runid):
        self.__failed_tests = None

        path, module, call = nose.util.test_address(case)
        id = self.__get_testcase_id(case)
        self.__sqlite.execute(
            'INSERT INTO failures (testid, runid, failtime) VALUES (?, ?, ?)',
            (id, runid, datetime.datetime.now())
        )

    def __get_testcase_id(self, case):
        path, module, call = nose.util.test_address(case)

        cur = self.__sqlite.execute(
            'SELECT id FROM tests WHERE path = ? AND module = ? AND call = ?',
            (path, module, call)
        )

        row = cur.fetchone()
        if row is None:
            cur = self.__sqlite.execute(
                'INSERT INTO tests (path, module, call) VALUES (?, ?, ?)',
                (path, module, call)
            )
            return cur.lastrowid

        return row[0]

    def __get_new_runid(self):
        cur = self.__sqlite.execute(
            'INSERT INTO runs (runtime) VALUES (?)',
            (datetime.datetime.now(),)
        )
        return cur.lastrowid

    def __get_last_runid(self):
        cur = self.__sqlite.execute('SELECT id FROM runs ORDER BY id DESC LIMIT 1')
        res = cur.fetchone()
        if res is None:
            return 0

        return res[0]

    def __load_failures(self):
        self.__failed_tests = {}
        cur = self.__sqlite.execute(
            'SELECT path, module, call, max(runid) FROM failures JOIN tests ' +
            'WHERE tests.id == failures.testid ' +
            'GROUP BY path, module, call;'
        )
        topid = self.__get_last_runid()

        for path, module, call, runid in cur:
            key = (path, module, call)
            new_run_id = topid - runid

            self.__failed_tests[key] = new_run_id

    def dump_info(self, stream=sys.stdout):
        cur = self.__sqlite.execute('SELECT count(*) FROM runs')
        runcount = cur.fetchone()[0]

        cur = self.__sqlite.execute(
            'SELECT path, module, call, count(*) AS failcount FROM failures JOIN tests ' +
            'WHERE tests.id == failures.testid ' +
            'GROUP BY path, module, call ' +
            'ORDER BY failcount DESC;'
        )

        for path, module, call, failcount in cur:
            print(
                '[{} / {}] {}:{}:{}'.format(
                    failcount, runcount, path, module, call
                ),
                file=stream
            )


def quicktest_statistics():
    import argparse

    parser = argparse.ArgumentParser(
        description='Statistic analizer for the quicktester nose plugins'
    )

    parser.add_argument('-f', '--file', default=DEFAULT_STATISTICS_FILE,
                        help='Statistics file (default: %(default)s')

    options = parser.parse_args()

    Statistic(options.file).dump_info()
    return 0
