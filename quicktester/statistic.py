from __future__ import print_function

import sys
import json
import nose
import os.path
import datetime
import sqlite3
import collections

from . import util


class Report(object):
    Status = collections.namedtuple('Status', ['id', 'code', 'name', 'failing'])

    STATUS_PASSED = Status(0, '.', 'passed', False)
    STATUS_FAILED = Status(1, 'F', 'failed', True)
    STATUS_ERROR = Status(2, 'E', 'error', True)
    STATUS_SKIPPED = Status(3, 'S', 'skipped', False)

    __status_ids = {
        status.id: status for status in {STATUS_PASSED, STATUS_FAILED, STATUS_ERROR, STATUS_SKIPPED}
    }

    @classmethod
    def get_status_by_id(cls, id):
        return cls.__status_ids[id]

    @classmethod
    def get_failing_ids(cls):
        return {id for id, status in cls.__status_ids.items() if status.failing}

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
        self.__failure_sets = {}

    def report_run(self, report):
        self.__failure_sets.clear()
        self.__database.report_run(report)

    def check_if_failed(self, obj, backlog):
        self.__verify_backlog(backlog)
        if backlog not in self.__failure_sets:
            self.__failure_sets[backlog] = self.__database.get_failure_set(backlog)

        return nose.util.test_address(obj) in self.__failure_sets[backlog]

    def get_failure_paths(self, backlog):
        self.__verify_backlog(backlog)
        return set(path for path, _, _ in self.__database.get_failure_set(backlog))

    def dump_info(self, backlog, relto='.', dump_all=False, failonly=False, file=sys.stdout):
        self.__verify_backlog(backlog)
        last_runid = self.__database.get_last_runid()

        display_range = (last_runid - backlog + 1, last_runid)
        test_runs = {}

        for runid in range(display_range[0], display_range[1] + 1):
            if runid < 0:
                continue

            for path, module, call, status in self.__database.get_run(runid):
                if not dump_all and not util.is_reldir(path, relto):
                    continue

                addr = (path, module, call)
                test_runs.setdefault(addr, {})
                test_runs[addr][runid] = status

        if failonly:
            test_runs = self.__filter_has_failing(test_runs)

        keys = list(test_runs.keys())
        keys.sort(key=self.__sanitize_address)

        count = 0
        for path, module, call in keys:
            key = (path, module, call)
            runbar = self.__get_runbar(test_runs[key], display_range)

            address = self.__sanitize_address((os.path.relpath(path, relto), module, call))

            print('[{}] {}'.format(runbar, address), file=file)
            count += 1

        if count:
            print(file=file)

        print('{} test(s) out of {} shown'.format(count, self.__database.get_test_count()), file=file)

    def __sanitize_address(self, key):
        path, module, call = key
        if call is None:
            return path + ':' + module

        return ':'.join(key)

    def __filter_has_failing(self, runs):
        has_failing = set()
        for addr, run in runs.items():
            if any(status.failing for status in run.values()):
                has_failing.add(addr)

        return {addr: run for addr, run in runs.items() if addr in has_failing}

    def __verify_backlog(self, backlog):
        if backlog <= 0:
            raise ValueError('Backlog must be greater than 0')

    def __get_runbar(self, test_run, display_range):
        res = []
        for runid in range(display_range[0], display_range[1] + 1):
            if runid not in test_run:
                res.append(' ')
                continue

            res.append(test_run[runid].code)

        return ''.join(res)


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
        failure_ids = tuple(Report.get_failing_ids())
        failure_conds = ' OR '.join(['result.statusid == ?'] * len(failure_ids))

        last_runid = self.get_last_runid()
        cur = self.__connection.execute(
            'SELECT path, module, call, max(runid) AS maxid FROM result JOIN test ' +
            'WHERE test.id == result.testid AND ({}) '.format(failure_conds) +
            'GROUP BY path, module, call;',
            failure_ids
        )

        return set((path, module, call) for path, module, call, maxid in cur if last_runid - maxid < backlog)

    def get_run(self, runid):
        last_runid = self.get_last_runid()
        cur = self.__connection.execute(
            'SELECT path, module, call, statusid FROM result JOIN test ' +
            'WHERE test.id == result.testid AND runid == ?' +
            'ORDER BY runid ASC',
            (runid,)
        )

        for path, module, call, statusid in cur:
            yield path, module, call, Report.get_status_by_id(statusid)

    def get_test_count(self):
        cur = self.__connection.execute('SELECT count(*) FROM test')
        return cur.fetchone()[0]

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
