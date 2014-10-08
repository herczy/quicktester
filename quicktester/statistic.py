from __future__ import print_function

import sys
import json
import nose
import os.path
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
        self.__connection = self.__init_connection()

    def report_result(self, result):
        try:
            runid = self.__get_new_runid()

            for failure, _ in result.failures:
                self.__report_failure(failure, runid)

            for error, _ in result.errors:
                self.__report_failure(error, runid)

        except:
            self.__connection.rollback()
            raise

        self.__connection.commit()

    def check_if_failed(self, obj, backlog):
        return nose.util.test_address(obj) in self.__get_failure_set(backlog)

    def get_failure_paths(self, backlog):
        return set(path for path, _, _ in self.__get_failure_set(backlog))

    def dump_info(self, backlog, relto='.', file=sys.stdout):
        test_run_ids = {}
        last_runid = self.__get_last_runid()

        for path, module, call, runid in self.__get_runs(backlog):
            key = (path, module, call)
            test_run_ids.setdefault(key, set())
            test_run_ids[key].add(runid)

        keys = list(test_run_ids.keys())
        keys.sort()

        for path, module, call in keys:
            key = (path, module, call)
            runbar = self.__get_runbar(test_run_ids[key], backlog, last_runid)

            print('[{}] {}:{}:{}'.format(runbar, os.path.relpath(path, relto), module, call), file=file)

    def __get_runbar(self, test_run_ids, backlog, last_runid):
        res = []
        for index in range(backlog):
            if last_runid <= index:
                res.append(' ')
                continue

            if index in test_run_ids:
                res.append('F')

            else:
                res.append('.')

        return ''.join(reversed(res))

    ##
    ## Database functions
    ##

    def __report_failure(self, case, runid):
        path, module, call = nose.util.test_address(case)
        id = self.__get_testcase_id(case)

        self.__connection.execute(
            'INSERT INTO failures (testid, runid, failtime) VALUES (?, ?, ?)',
            (id, runid, datetime.datetime.now())
        )

    def __get_testcase_id(self, case):
        path, module, call = nose.util.test_address(case)

        cur = self.__connection.execute(
            'SELECT id FROM tests WHERE path = ? AND module = ? AND call = ?',
            (path, module, call)
        )

        row = cur.fetchone()
        if row is None:
            cur = self.__connection.execute(
                'INSERT INTO tests (path, module, call) VALUES (?, ?, ?)',
                (path, module, call)
            )
            return cur.lastrowid

        return row[0]

    def __get_new_runid(self):
        cur = self.__connection.execute(
            'INSERT INTO runs (runtime) VALUES (?)',
            (datetime.datetime.now(),)
        )
        return cur.lastrowid

    def __get_last_runid(self):
        cur = self.__connection.execute('SELECT id FROM runs ORDER BY id DESC LIMIT 1')
        res = cur.fetchone()
        if res is None:
            return 0

        return res[0]

    def __get_failure_set(self, backlog):
        if backlog <= 0:
            raise ValueError('Backlog must be bigger than zero')

        last_runid = self.__get_last_runid()
        cur = self.__connection.execute(
            'SELECT path, module, call, max(runid) AS maxid FROM failures JOIN tests ' +
            'WHERE tests.id == failures.testid ' +
            'GROUP BY path, module, call;'
        )

        return set((path, module, call) for path, module, call, maxid in cur if last_runid - maxid < backlog)

    def __get_runs(self, backlog):
        if backlog <= 0:
            raise ValueError('Backlog must be bigger than zero')

        last_runid = self.__get_last_runid()
        cur = self.__connection.execute(
            'SELECT path, module, call, runid FROM failures JOIN tests ' +
            'WHERE tests.id == failures.testid AND runid >= ?',
            (last_runid - backlog + 1,)
        )

        for path, module, call, runid in cur:
            yield path, module, call, last_runid - runid

    ##
    ## Connection initialization
    ##

    def __init_connection(self):
        if self.__filename is None or not os.path.isfile(self.__filename):
            return self.__create_connection()

        return self.__connect()

    def __create_connection(self):
        sqlite = self.__connect()

        sqlite.execute(TABLE_DEF_TESTS)
        sqlite.execute(TABLE_DEF_FAILURES)
        sqlite.execute(TABLE_DEF_RUN)
        sqlite.commit()

        return sqlite

    def __connect(self):
        return sqlite3.connect(self.__filename or ':memory:')
