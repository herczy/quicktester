from __future__ import print_function

import os.path
import sys
import shlex
import shutil
import subprocess

from .assertfunc import Assert
from .path import tools_path, git_repo_path
from .verify import verify_context

if sys.version_info.major == 2:
    string_types = (str, unicode)

else:
    string_types = str


def ident(text, ident=4):
    res = []
    for line in text.split('\n'):
        if not line.strip():
            res.append('')
            continue

        res.append((' ' * ident) + line.rstrip())

    return '\n'.join(res)


class Result(object):
    def __init__(self, command, returncode, stdout, stderr):
        self.command = command
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def dump(self, file=sys.stdout):
        print('----- BEGIN COMMAND RESULTS -----', file=file)
        print('Command:', self.command, file=file)
        print('Return code:', self.returncode, file=file)

        print('Standard output:', file=file)
        print(ident('----- BEGIN STDOUT -----'), file=file)
        print(ident(self.stdout), file=file)
        print(ident('----- END STDOUT -----'), file=file)

        print('Standard error output:', file=file)
        print(ident('----- BEGIN STDERR -----'), file=file)
        print(ident(self.stderr), file=file)
        print(ident('----- END STDERR -----'), file=file)

        print('----- END COMMAND RESULTS -----', file=file)


class Command(object):
    group = None
    ignore_result = False

    def execute(self):
        raise NotImplementedError('{}.execute'.format(type(self).__name__))

    def __repr__(self):
        return '<command 0x{:x}>'.format(id(self))


class SystemCommand(Command):
    def __init__(self, command, env=None):
        self.command = list(command)
        self.env = env

    def execute(self):
        process = subprocess.Popen(
            self.command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=self.env,
            universal_newlines=True
        )

        stdout, stderr = process.communicate()

        return Result(self, process.returncode, stdout.rstrip(), stderr.rstrip())

    def __repr__(self):
        cmd = ' '.join(repr(arg) for arg in self.command)
        return '<system command {}>'.format(cmd)


class PythonCommand(SystemCommand):
    group = 'python'

    def __init__(self, command, env=None):
        command = [sys.executable, '-B'] + list(command)

        env = dict(env or os.environ)
        self.__append_env_path(env, 'PYTHONPATH', git_repo_path)

        super(PythonCommand, self).__init__(command, env=env)

    def __append_env_path(self, environ, dest, path, sep=':'):
        paths = environ.get(dest, None)
        if paths is None:
            paths = []

        else:
            paths = paths.split(sep)

        paths.append(path)
        environ[dest] = ':'.join(paths)


class ToolCommand(PythonCommand):
    group = 'tool'

    def __init__(self, command, env=None):
        name = command[0]
        extra_args = list(command[1:])

        super(ToolCommand, self).__init__(
            [os.path.join(tools_path, name + '.py')] + list(extra_args),
            env=env
        )


class EggBuildCommand(PythonCommand):
    ignore_result = True

    def __init__(self, dest, environ):
        super(EggBuildCommand, self).__init__(['setup.py', 'bdist_egg', '--dist', dest])

        self.__environ = environ

    def execute(self):
        self.__environ.exit()
        try:
            res = super(EggBuildCommand, self).execute()
            shutil.rmtree('build', ignore_errors=True)
            shutil.rmtree('quicktester.egg-info', ignore_errors=True)

        finally:
            self.__environ.enter()

        self.__assert_plugins_exits()
        return res

    def __assert_plugins_exits(self):
        result = ToolCommand(['get-installed-nose-plugins']).execute()
        plugins = set(plugin.split(' = ', 1)[0] for plugin in result.stdout.strip().split('\n'))

        try:
            for expected_plugin in {'statistic', 'fail-only', 'git-change'}:
                Assert._in(expected_plugin, plugins)

        except:
            result.dump()
            raise


class CustomCommand(Command):
    ignore_result = True

    def __init__(self, command, env=None):
        super(CustomCommand, self).__init__()

        self.__environment = env

    def _run_command(self, command):
        result = SystemCommand(shlex.split(command), env=self.__environment).execute()
        Assert.equal(0, result.returncode)


class GitInitCommand(CustomCommand):
    def execute(self):
        self._run_command('git init .')
        self._run_command('git config user.name "Viktor Hercinger"')
        self._run_command('git config user.email "hercinger.viktor@gmail.com"')


class GitCommitCommand(CustomCommand):
    def execute(self):
        self._run_command('git add .')
        self._run_command('git commit -m commit')


class Runner(object):
    HUMAN_READABLE_INDEXES = {
        'first': 0,
        'last': -1,
    }

    COMMAND_CLASS_MAPPING = {
        'quicktester-statistics': ToolCommand,
        'nosetests': ToolCommand,
        'git-init': GitInitCommand,
        'git-commit': GitCommitCommand,
    }

    DEFAULT_COMMAND_CLASS = SystemCommand

    def __init__(self):
        self.results = []

    def execute(self, command):
        result = command.execute()
        if not command.ignore_result:
            self.results.append(result)

    def filter_results(self, group=None):
        if group is None:
            return self.results

        return [result for result in self.results if result.command.group == group]

    def get_result(self, index, group=None):
        if isinstance(index, string_types):
            if not index in self.HUMAN_READABLE_INDEXES:
                raise AssertionError("Unknown human-readable index {!r}".format(index))

            index = self.HUMAN_READABLE_INDEXES[index]

        return self.filter_results(group)[index]

    @classmethod
    def create_command(cls, command, *args, **kwargs):
        command = shlex.split(command)
        command_cls = cls.COMMAND_CLASS_MAPPING.get(command[0], cls.DEFAULT_COMMAND_CLASS)

        return command_cls(command, *args, **kwargs)


def verify_runner(context):
    verify_context(context, 'runner', msg='initialize_runner_context() has not been yet called')


def initialize_runner_context(context):
    context.runner = Runner()


def execute_command(context, command, repeat=1):
    verify_runner(context)

    if not isinstance(command, Command):
        command = Runner.create_command(command)

    for _ in range(repeat):
        context.runner.execute(command)


def get_result(context, index, group=None):
    verify_runner(context)

    return context.runner.get_result(index, group=group)


def __assert_result(context, attribute, expected, index, group=None):
    result = get_result(context, index, group=group)
    try:
        Assert.equal(expected, getattr(result, attribute))

    except:
        result.dump()
        raise


def assert_return_code(context, expected_return_code, index, group=None):
    __assert_result(context, 'returncode', expected_return_code, index, group=group)


def assert_stdout(context, expected_stdout, index, group=None):
    __assert_result(context, 'stdout', expected_stdout, index, group=group)


def assert_stderr(context, expected_stderr, index, group=None):
    __assert_result(context, 'stderr', expected_stderr, index, group=group)
