from __future__ import print_function

import sys
import json
import nose
import os.path
import datetime
import sqlite3


class Statistic(object):
    def __init__(self, filename, dbfactory=None):
        if dbfactory is None:
            dbfactory = DatabaseFactory()

        self.__database = dbfactory.init_connection(filename)

    def report_result(self, result):
        self.__database.report_failures(case for case, _ in (result.failures + result.errors))

    def check_if_failed(self, obj, backlog):
        self.__verify_backlog(backlog)
        return nose.util.test_address(obj) in self.__database.get_failure_set(backlog)

    def get_failure_paths(self, backlog):
        self.__verify_backlog(backlog)
        return set(path for path, _, _ in self.__database.get_failure_set(backlog))

    def dump_info(self, backlog, relto='.', file=sys.stdout):
        self.__verify_backlog(backlog)
        test_run_ids = {}
        last_runid = self.__database.get_last_runid()

        for path, module, call, runid in self.__database.get_runs(backlog):
            key = (path, module, call)
            test_run_ids.setdefault(key, set())
            test_run_ids[key].add(runid)

        keys = list(test_run_ids.keys())
        keys.sort()

        for path, module, call in keys:
            key = (path, module, call)
            runbar = self.__get_runbar(test_run_ids[key], backlog, last_runid)

            print('[{}] {}:{}:{}'.format(runbar, os.path.relpath(path, relto), module, call), file=file)

    def __verify_backlog(self, backlog):
        if backlog <= 0:
            raise ValueError('Backlog must be greater than 0')

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


class _RunContext(object):
    def __init__(self, connection):
        self.__connection = connection
        self.__runid = None

    def __enter__(self):
        self.__runid = self.__get_new_runid()
        return self

    def __exit__(self, exc_type, exc_value, trace):
        if exc_type is not None:
            self.__connection.rollback()

        else:
            self.__connection.commit()

    def report_failure(self, case):
        addr = nose.util.test_address(case)
        return self.__report_failure_address(addr)

    def __report_failure_address(self, addr):
        path, module, call = addr
        id = self.__get_testcase_id(addr)

        self.__connection.execute(
            'INSERT INTO failures (testid, runid, failtime) VALUES (?, ?, ?)',
            (id, self.__runid, datetime.datetime.now())
        )

    def __get_testcase_id(self, addr):
        addr = tuple(addr)
        cur = self.__connection.execute('SELECT id FROM tests WHERE path = ? AND module = ? AND call = ?', addr)

        row = cur.fetchone()
        if row is None:
            cur = self.__connection.execute('INSERT INTO tests (path, module, call) VALUES (?, ?, ?)', addr)
            return cur.lastrowid

        return row[0]

    def __get_new_runid(self):
        cur = self.__connection.execute(
            'INSERT INTO runs (runtime) VALUES (?)',
            (datetime.datetime.now(),)
        )
        return cur.lastrowid


class _Database(object):
    def __init__(self, connection):
        self.__connection = connection

    def report_failures(self, failures):
        with _RunContext(self.__connection) as runctx:
            for failure in failures:
                runctx.report_failure(failure)

    def get_last_runid(self):
        cur = self.__connection.execute('SELECT id FROM runs ORDER BY id DESC LIMIT 1')
        res = cur.fetchone()
        if res is None:
            return 0

        return res[0]

    def get_failure_set(self, backlog):
        last_runid = self.get_last_runid()
        cur = self.__connection.execute(
            'SELECT path, module, call, max(runid) AS maxid FROM failures JOIN tests ' +
            'WHERE tests.id == failures.testid ' +
            'GROUP BY path, module, call;'
        )

        return set((path, module, call) for path, module, call, maxid in cur if last_runid - maxid < backlog)

    def get_runs(self, backlog):
        last_runid = self.get_last_runid()
        cur = self.__connection.execute(
            'SELECT path, module, call, runid FROM failures JOIN tests ' +
            'WHERE tests.id == failures.testid AND runid >= ? ' +
            'ORDER BY runid ASC',
            (last_runid - backlog + 1,)
        )

        for path, module, call, runid in cur:
            yield path, module, call, last_runid - runid


class DatabaseFactory(object):
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

    def init_connection(self, filename):
        if filename is None or not os.path.isfile(filename):
            return _Database(self.__create_database(filename))

        if not self.__is_legacy_format(filename):
            return _Database(self.__connect(filename))

        runs = self.__load_legacy_data(filename)
        os.rename(filename, filename + '~')

        res = _Database(self.__create_database(filename))
        for run in runs:
            res.report_failures(_Address(case) for case in run)

        return res

    def __create_database(self, filename):
        sqlite = self.__connect(filename)

        sqlite.execute(self.TABLE_DEF_TESTS)
        sqlite.execute(self.TABLE_DEF_FAILURES)
        sqlite.execute(self.TABLE_DEF_RUN)
        sqlite.commit()

        return sqlite

    def __connect(self, filename):
        return sqlite3.connect(filename or ':memory:')

    def __is_legacy_format(self, filename):
        with open(filename, 'rb') as f:
            return f.read(3) in {b'[[[', b'[[]'}

    def __load_legacy_data(self, filename):
        if filename is None or not os.path.isfile(filename):
            return []

        with open(filename, 'r') as f:
            return [[tuple(str(c) for c in address) for address in run] for run in json.load(f)]


class _Address(object):
    def __init__(self, address):
        self.__address = address

    def address(self):
        return self.__address
