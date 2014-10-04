import re
import os.path
import sys
import shlex
import subprocess
import unittest


tools_path = os.path.abspath(os.path.join(__file__, '..', '..', 'tools'))
git_repo_path = os.path.abspath(os.path.join(__file__, '..', '..', '..'))
caps = re.compile('([A-Z])')
prefix = 'assert_'


def __make_assert_class():
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
    for attribute in dir(dummy):
        if not attribute.startswith('assert') or '_' in attribute:
            continue

        assert_dict[make_pep8_name(attribute)] = make_caller(dummy, attribute)

    return type('Assert', (object,), assert_dict)


Assert = __make_assert_class()
del __make_assert_class


try:
    sys.path.insert(0, git_repo_path)
    import quicktester

finally:
    sys.path.remove(git_repo_path)


def append_env_path(environ, dest, path, sep=':'):
    paths = environ.get(dest, None)
    if paths is None:
        paths = []

    else:
        paths = paths.split(sep)

    paths.append(path)
    environ[dest] = ':'.join(paths)


def run_tool(name, args):
    if args is None:
        args = []

    else:
        args = shlex.split(args)

    env = dict(os.environ)
    append_env_path(env, 'PYTHONPATH', git_repo_path)

    path = os.path.join(tools_path, name + '.py')
    process = subprocess.Popen(
        [sys.executable, path] + args,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        universal_newlines=True
    )
    stdout, stderr = process.communicate()

    return stdout, stderr, process.returncode


def run_quicktester_statistics(cli_args=None):
    stdout, stderr, rc = run_tool('quicktester-statistics', cli_args)
    if rc != 0:
        print('----- BEGIN STDERR OUTPUT -----')
        print(stderr)
        print('----- END STDERR OUTPUT -----')

    Assert.equal(0, rc)

    return stdout
