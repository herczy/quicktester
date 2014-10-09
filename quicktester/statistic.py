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
            dbfactory = _DatabaseFactory

        self.__database = dbfactory(filename).init_connection()

    def report_result(self, result):
        self.__database.report_failures(case for case, _ in (result.failures + result.errors))

    def check_if_failed(self, obj, backlog):
        return nose.util.test_address(obj) in self.__database.get_failure_set(backlog)

    def get_failure_paths(self, backlog):
        return set(path for path, _, _ in self.__database.get_failure_set(backlog))

    def dump_info(self, backlog, relto='.', file=sys.stdout):
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


class _Database(object):
    def __init__(self, connection):
        self.__connection = connection

    def report_failures(self, failures):
        try:
            runid = self.__get_new_runid()

            for failure in failures:
                self.__report_failure(failure, runid)

        except:
            self.__connection.rollback()
            raise

        self.__connection.commit()

    def get_last_runid(self):
        cur = self.__connection.execute('SELECT id FROM runs ORDER BY id DESC LIMIT 1')
        res = cur.fetchone()
        if res is None:
            return 0

        return res[0]

    def get_failure_set(self, backlog):
        if backlog <= 0:
            raise ValueError('Backlog must be bigger than zero')

        last_runid = self.get_last_runid()
        cur = self.__connection.execute(
            'SELECT path, module, call, max(runid) AS maxid FROM failures JOIN tests ' +
            'WHERE tests.id == failures.testid ' +
            'GROUP BY path, module, call;'
        )

        return set((path, module, call) for path, module, call, maxid in cur if last_runid - maxid < backlog)

    def get_runs(self, backlog):
        if backlog <= 0:
            raise ValueError('Backlog must be bigger than zero')

        last_runid = self.get_last_runid()
        cur = self.__connection.execute(
            'SELECT path, module, call, runid FROM failures JOIN tests ' +
            'WHERE tests.id == failures.testid AND runid >= ?',
            (last_runid - backlog + 1,)
        )

        for path, module, call, runid in cur:
            yield path, module, call, last_runid - runid

    def __report_failure(self, case, runid):
        addr = nose.util.test_address(case)
        return self.__report_failure_address(addr, runid)

    def __report_failure_address(self, addr, runid):
        path, module, call = addr
        id = self.__get_testcase_id(addr)

        self.__connection.execute(
            'INSERT INTO failures (testid, runid, failtime) VALUES (?, ?, ?)',
            (id, runid, datetime.datetime.now())
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


class _DatabaseFactory(object):
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

    def __init__(self, filename):
        self.__filename = filename

    def init_connection(self):
        if self.__filename is None or not os.path.isfile(self.__filename):
            return _Database(self.__create_database())

        if not self.__is_legacy_format():
            return _Database(self.__connect())

        runs = self.__load_legacy_data()
        os.rename(self.__filename, self.__filename + '~')

        res = _Database(self.__create_database())
        for run in runs:
            res.report_failures(_Address(case) for case in run)

        return res

    def __create_database(self):
        sqlite = self.__connect()

        sqlite.execute(self.TABLE_DEF_TESTS)
        sqlite.execute(self.TABLE_DEF_FAILURES)
        sqlite.execute(self.TABLE_DEF_RUN)
        sqlite.commit()

        return sqlite

    def __connect(self):
        return sqlite3.connect(self.__filename or ':memory:')

    def __is_legacy_format(self):
        with open(self.__filename, 'rb') as f:
            return f.read(3) in {b'[[[', b'[[]'}

    def __load_legacy_data(self):
        if self.__filename is None or not os.path.isfile(self.__filename):
            return []

        with open(self.__filename, 'r') as f:
            return [[tuple(str(c) for c in address) for address in run] for run in json.load(f)]


class _Address(object):
    def __init__(self, address):
        self.__address = address

    def address(self):
        return self.__address
