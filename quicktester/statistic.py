from __future__ import print_function

import os.path
import json
import nose
import datetime

import sqlite3


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

        exists = os.path.isfile(self.__filename)
        self.__sqlite = sqlite3.connect(self.__filename)
        if not exists:
            self.__create_table()

    def __create_table(self):
        self.__sqlite.execute(TABLE_DEF_TESTS)
        self.__sqlite.execute(TABLE_DEF_FAILURES)
        self.__sqlite.execute(TABLE_DEF_RUN)
        self.__sqlite.commit()

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

    def __report_failure(self, case, runid):
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

    def __get_failure_counts(self):
        cur = self.__sqlite.execute(
            'SELECT path, module, call, count(*) AS failcount FROM failures JOIN tests ' +
            'WHERE tests.id == failures.testid ' +
            'GROUP BY path, module, call ' +
            'ORDER BY failcount DESC;'
        )

        for path, module, call, failcount in cur:
            yield (path, module, call), failcount

    def order_by_failure(self, cases):
        case_map = {nose.util.test_address(case): case for case in cases}
        failures = []

        for address, _ in self.__get_failure_counts():
            if address not in case_map:
                continue

            case = case_map[address]
            del case_map[address]
            failures.append(case)

        return failures, list(case_map.values())
