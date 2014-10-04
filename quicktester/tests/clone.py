import unittest
import os.path
import tempfile
import shutil
import shlex
import subprocess
import functools

import quicktester


class _TemporaryClone(object):
    name = None
    clone_repo = os.path.abspath(os.path.join(quicktester.__file__, '..', '..'))

    def __enter__(self):
        self.name = tempfile.mkdtemp()
        self.oldcwd = os.getcwd()

        self.__execute('git clone "{0}" "{1}"'.format(self.clone_repo, self.name))
        os.chdir(self.name)
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
        subprocess.check_call(shlex.split(command))


class RepoTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(RepoTestCase, self).__init__(*args, **kwargs)

        self.__testfunc = getattr(self, self._testMethodName)

        @functools.wraps(self.__testfunc)
        def _wrapped_runner():
            with _TemporaryClone() as clone:
                self.clone = clone
                try:
                    return self.__testfunc()

                finally:
                    self.clone = None

        setattr(self, self._testMethodName, _wrapped_runner)
