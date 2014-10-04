from __future__ import print_function

import sys
import json
import nose
import os.path


class Statistic(object):
    def __init__(self, filename):
        self.__filename = filename
        self.__runs = self.__load_data()

    def report_result(self, result):
        fail_paths = []

        for failure, _ in result.failures:
            fail_paths.append(nose.util.test_address(failure))

        for error, _ in result.errors:
            fail_paths.append(nose.util.test_address(error))

        self.__runs.append(fail_paths)
        self.__save_data(self.__runs)

    def check_if_failed(self, obj, backlog):
        restricted_set = self.__get_restricted_set(backlog)
        address = nose.util.test_address(obj)
        return any(address in run for run in restricted_set)

    def get_failure_paths(self, backlog):
        restricted_set = self.__get_restricted_set(backlog)
        return [path for fail_paths in restricted_set for path, _, _ in fail_paths]

    def dump_info(self, backlog, relto='.', file=sys.stdout):
        restricted_set = self.__get_restricted_set(backlog)
        test_run_ids = {}

        for index, run in enumerate(self.__runs):
            for addr in run:
                test_run_ids.setdefault(addr, set())
                test_run_ids[addr].add(index - len(self.__runs) + backlog)

        keys = list(test_run_ids.keys())
        keys.sort()

        for path, module, call in keys:
            runbar = self.__get_runbar(test_run_ids[addr], backlog)

            print('[{}] {}:{}:{}'.format(runbar, os.path.relpath(path, relto), module, call), file=file)

    def __get_restricted_set(self, backlog):
        if backlog <= 0:
            raise ValueError('Backlog must be bigger than zero')

        return self.__runs[- backlog:]

    def __get_runbar(self, test_run_ids, backlog):
        res = []
        top = len(self.__runs)
        for index in range(backlog):
            if top - backlog + index < 0:
                res.append(' ')
                continue

            if index in test_run_ids:
                res.append('F')

            else:
                res.append('.')

        return ''.join(res)

    def __load_data(self):
        if self.__filename is None or not os.path.isfile(self.__filename):
            return []

        with open(self.__filename, 'r') as f:
            return [[tuple(address) for address in run] for run in json.load(f)]

    def __save_data(self, data):
        if self.__filename is not None:
            with open(self.__filename, 'w') as f:
                json.dump(data, f)
