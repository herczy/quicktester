from __future__ import print_function

import sys
import json
import nose
import os.path
import datetime
import sqlite3
import collections


class Report(object):
    Status = collections.namedtuple('Status', ['id', 'code', 'name'])

    STATUS_PASSED = Status(0, '.', 'passed')
    STATUS_FAILED = Status(1, 'F', 'failed')
    STATUS_ERROR = Status(2, 'E', 'error')
    STATUS_SKIPPED = Status(3, 'S', 'skipped')

    __status_ids = {
        status.id: status for status in {STATUS_PASSED, STATUS_FAILED, STATUS_ERROR, STATUS_SKIPPED}
    }

    @classmethod
    def get_status_by_id(cls, id):
        return cls.__status_ids[id]

    def __init__(self):
        self.__cases = []

    def add(self, case, status):
        self.__cases.append((case, status))

    def __iter__(self):
        return iter(self.__cases)


class Statistic(object):
    def __init__(self, filename, dbfactory=None):
        if dbfactory is None:
            dbfactory = DatabaseFactory()

        self.__database = dbfactory.init_connection(filename)

    def report_result(self, result):
        run_data = []
        for error, _ in result.errors:
            run_data.append((error, Report.STATUS_ERROR))

        for failure, _ in result.failures:
            run_data.append((failure, Report.STATUS_FAILED))

        self.__database.report_run(run_data)

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


class _Database(object):
    def __init__(self, connection):
        self.__connection = connection

    def report_run(self, cases):
        try:
            runid = self.__get_new_runid()

            for case, status in cases:
                self.__report_case(case, status, runid)

        except:
            self.__connection.rollback()
            raise

        self.__connection.commit()

    def get_last_runid(self):
        cur = self.__connection.execute('SELECT id FROM run ORDER BY id DESC LIMIT 1')
        res = cur.fetchone()
        if res is None:
            return 0

        return res[0]

    def get_failure_set(self, backlog):
        last_runid = self.get_last_runid()
        cur = self.__connection.execute(
            'SELECT path, module, call, max(runid) AS maxid FROM result JOIN test ' +
            'WHERE test.id == result.testid AND result.statusid == ?' +
            'GROUP BY path, module, call;',
            (Report.STATUS_FAILED.id,)
        )

        return set((path, module, call) for path, module, call, maxid in cur if last_runid - maxid < backlog)

    def get_runs(self, backlog):
        last_runid = self.get_last_runid()
        cur = self.__connection.execute(
            'SELECT path, module, call, runid FROM result JOIN test ' +
            'WHERE test.id == result.testid AND runid >= ? AND result.statusid = ?' +
            'ORDER BY runid ASC',
            (last_runid - backlog + 1, Report.STATUS_FAILED.id)
        )

        for path, module, call, runid in cur:
            yield path, module, call, last_runid - runid

    def __report_case(self, case, status, runid):
        addr = nose.util.test_address(case)
        return self.__report_case_address(addr, status, runid)

    def __report_case_address(self, addr, status, runid):
        path, module, call = addr
        id = self.__get_testcase_id(addr)

        self.__connection.execute(
            'INSERT INTO result (testid, runid, statusid, time) VALUES (?, ?, ?, ?)',
            (id, runid, status.id, datetime.datetime.now())
        )

    def __get_testcase_id(self, addr):
        addr = tuple(addr)
        cur = self.__connection.execute('SELECT id FROM test WHERE path = ? AND module = ? AND call = ?', addr)

        row = cur.fetchone()
        if row is None:
            cur = self.__connection.execute('INSERT INTO test (path, module, call) VALUES (?, ?, ?)', addr)
            return cur.lastrowid

        return row[0]

    def __get_new_runid(self):
        cur = self.__connection.execute(
            'INSERT INTO run (runtime) VALUES (?)',
            (datetime.datetime.now(),)
        )
        return cur.lastrowid


class DatabaseFactory(object):
    TABLE_DEF_TEST = '''
        CREATE TABLE test (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT,
            module TEXT,
            call TEXT
        );
    '''

    TABLE_DEF_RUN = '''
        CREATE TABLE run (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            runtime DATETIME
        );
    '''

    TABLE_DEF_RESULT = '''
        CREATE TABLE result (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            testid INTEGER REFERENCES test (id),
            runid INTEGER REFERENCES run (id),
            statusid INTEGER,
            time DATETIME
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
            res.report_run((_Address(case), Report.STATUS_FAILED) for case in run)

        return res

    def __create_database(self, filename):
        sqlite = self.__connect(filename)

        sqlite.execute(self.TABLE_DEF_TEST)
        sqlite.execute(self.TABLE_DEF_RUN)
        sqlite.execute(self.TABLE_DEF_RESULT)
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
