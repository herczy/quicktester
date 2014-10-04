import re
import os.path
import sys
import shlex
import subprocess
import unittest
import pkg_resources

tools_path = os.path.abspath(os.path.join(__file__, '..', '..', 'tools'))
git_repo_path = os.path.abspath(os.path.join(__file__, '..', '..', '..'))

try:
    sys.path.insert(0, git_repo_path)
    import quicktester

finally:
    sys.path.remove(git_repo_path)


def __make_assert_class():
    caps = re.compile('([A-Z])')
    prefix = 'assert_'

    def make_pep8_name(name):
        sub = caps.sub(lambda m: '_' + m.groups()[0].lower(), name)
        return sub[len(prefix):]

    def make_caller(obj, name):
        def func(cls, *args, **kwargs):
            return getattr(obj, name)(*args, **kwargs)

        return classmethod(func)

    class Dummy(unittest.TestCase):
        def nop():
            pass

    assert_dict = {}
    dummy = Dummy('nop')
    dummy.maxDiff = None
    for attribute in dir(dummy):
        if not attribute.startswith('assert') or '_' in attribute:
            continue

        assert_dict[make_pep8_name(attribute)] = make_caller(dummy, attribute)

    return type('Assert', (object,), assert_dict)


Assert = __make_assert_class()
del __make_assert_class


def append_env_path(environ, dest, path, sep=':'):
    paths = environ.get(dest, None)
    if paths is None:
        paths = []

    else:
        paths = paths.split(sep)

    paths.append(path)
    environ[dest] = ':'.join(paths)


def run(command, expected_rc=0):
    env = dict(os.environ)
    append_env_path(env, 'PYTHONPATH', git_repo_path)

    process = subprocess.Popen(
        [sys.executable] + command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        universal_newlines=True
    )

    stdout, stderr = process.communicate()
    if process.returncode != expected_rc:
        print('----- BEGIN STDERR OUTPUT -----')
        print(stderr)
        print('----- END STDERR OUTPUT -----')

    Assert.equal(expected_rc, process.returncode)

    return stdout, stderr


def run_tool(name, args, expected_rc=0):
    if args is None:
        args = []

    else:
        args = shlex.split(args)

    path = os.path.join(tools_path, name + '.py')
    return run([path] + args, expected_rc=expected_rc)


def run_quicktester_statistics(cli_args=None):
    return run_tool('quicktester-statistics', cli_args)[0]


def build_egg_file(dest):
    run(['setup.py', 'bdist_egg', '--dist', dest])


def run_nose(cli_args=None, expected_rc=0):
    return run_tool('nosetests', cli_args, expected_rc=expected_rc)[1]
