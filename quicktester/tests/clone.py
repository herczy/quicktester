from __future__ import print_function

import unittest
import os.path
import tempfile
import shutil
import shlex
import subprocess
import functools

import quicktester


class TemporaryClone(object):
    name = None
    clone_repo = os.path.abspath(os.path.join(quicktester.__file__, '..', '..'))

    def __enter__(self):
        self.name = tempfile.mkdtemp(prefix='quickrunner-clone-')
        self.oldcwd = os.getcwd()

        os.rmdir(self.name)
        shutil.copytree(self.oldcwd, self.name)

        os.chdir(self.name)
        self.__execute('git reset --hard')
        self.__execute('git clean -dfx')
        return self

    def __exit__(self, *args):
        os.chdir(self.oldcwd)
        shutil.rmtree(self.name, ignore_errors=True)
        self.name = None

    def get_path(self, path):
        return os.path.join(self.name, path)

    def open(self, path, *args, **kwargs):
        return open(self.get_path(path), *args, **kwargs)

    def write(self, path, content):
        with self.open(path, 'w') as f:
            f.write(content)

    def read(self, path):
        with self.open(path) as f:
            return f.read()

    def __execute(self, command):
        process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            self.__report_process_failure(command, stdout, stderr, process.returncode)
            raise AssertionError('Expected return code of command {!r} to be 0, got {}'.format(command, process.returncode))

        return stdout

    def __report_process_failure(self, command, stdout, stderr, returncode):
        print('Executed command:', command)
        print('Return code:', returncode)
        print('Stdout:')
        print(stdout)
        print('Stderr:')
        print(stderr)


class RepoTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(RepoTestCase, self).__init__(*args, **kwargs)

        self.__testfunc = getattr(self, self._testMethodName)

        @functools.wraps(self.__testfunc)
        def _wrapped_runner():
            with TemporaryClone() as clone:
                self.clone = clone
                try:
                    return self.__testfunc()

                finally:
                    self.clone = None

        setattr(self, self._testMethodName, _wrapped_runner)
