import sys
import os
import library


@given('an empty package "{package:w}"')
def step_impl(context, package):
    library.verify_environment(context)

    context.environment.write('{}/__init__.py'.format(package), '')
    context.environment.write('{}/tests/__init__.py'.format(package), '')


@given('the plugins are installed')
def step_impl(context):
    library.verify_environment(context)
    library.runner.verify_runner(context)

    library.runner.EggBuildCommand(os.getcwd(), context.environment).execute()


@when('the {kind:w} file "{filename}" is created')
@when('the {kind:w} file "{filename}" is changed')
@given('the {kind:w} file "{filename}" is created')
def step_impl(context, kind, filename):
    library.verify_environment(context)

    context.environment.write(filename, context.text)


@when('the command "{command}" is executed')
@when('the command "{command}" is executed {repeat:d} times')
@when('the command "{command}" is executed in "{where}"')
def step_impl(context, command, repeat=1, where='.'):
    library.runner.execute_command(context, command, repeat=repeat, where=where)


@then('the command does not print anything')
def step_impl(context):
    library.runner.assert_stdout(context, '', 'last')
    library.runner.assert_stderr(context, '', 'last')


@then('the following error message is given')
def step_impl(context):
    library.runner.assert_stderr(context, context.text, 'last')


@then('the {index:w} executed command prints the following')
def step_impl(context, index):
    library.runner.assert_stdout(context, context.text, index)
    library.runner.assert_stderr(context, '', index)


@then('the {index:w} executed command prints the following JSON')
def step_impl(context, index):
    library.runner.assert_stdout_json(context, context.text, index)
    library.runner.assert_stderr(context, '', index)


@then('the {index:w} executed command passes')
@then('the command fails with a code {code:d}')
@then('the command passes')
def step_impl(context, index='last', code=0):
    library.runner.assert_return_code(context, code, index)


@then('the last two executed commands pass')
def step_impl(context):
    library.runner.assert_return_code_range(context, 0, 'penultimate')


@then('only the "{fullname}" tests has beed rerun')
def step_impl(context, fullname):
    result = library.runner.get_result(context, 'last', group='tool')

    tests = library.process_nose_output(result.stderr)
    library.Assert.set_equal({fullname}, set(tests.keys()))


@given('a new repository is initialized with the new files')
def step_impl(context):
    library.runner.execute_command(context, 'git-init')
    library.runner.execute_command(context, 'git-commit')


@then('no tests are run')
def step_impl(context):
    result = library.runner.get_result(context, 'last', group='tool')

    tests = library.process_nose_output(result.stderr)
    library.Assert.list_equal([], list(tests.keys()))


@then('the following tests are run')
def step_impl(context):
    result = library.runner.get_result(context, 'last', group='tool')

    tests = library.process_nose_output(result.stderr)
    library.Assert.set_equal(
        set(context.text.split('\n')),
        set(tests.keys())
    )


def __ugly_hack_os_error_replacement(context):
    # Ugly hack: until Python 3.3, all there was is OSError's,
    # but now there is a PermissionError, so we need to fix this
    if sys.hexversion >= 0x03030000:
        context.text = context.text.replace('OSError', 'PermissionError')


@then('the quickfix file has the following content')
def step_impl(context):
    __ugly_hack_os_error_replacement(context)
    library.runner.assert_tempfile(context, 'QUICKFIX')


@then('the quickfix file contains the following line')
def step_impl(context):
    __ugly_hack_os_error_replacement(context)
    library.runner.assert_tempfile_contains(context, 'QUICKFIX')


@then('there are some other lines too')
def step_impl(context):
    library.runner.assert_tempfile_contains_others(context, 'QUICKFIX')
