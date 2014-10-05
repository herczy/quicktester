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
def step_impl(context, command, repeat=1):
    library.runner.execute_command(context, command, repeat=repeat)


@then('the command does not print anything')
def step_impl(context):
    library.runner.assert_stdout(context, '', 'last')
    library.runner.assert_stderr(context, '', 'last')


@then('the command passes')
def step_impl(context):
    library.runner.assert_return_code(context, 0, 'last')


@then('the {index:w} executed command prints the following')
def step_impl(context, index):
    library.runner.assert_stdout(context, context.text, 'last')
    library.runner.assert_stderr(context, '', 'last')


@then('the {index:w} executed command passes')
def step_impl(context, index):
    library.runner.assert_return_code(context, 0, index)


@then('only the "{fullname}" tests has beed rerun')
def step_impl(context, fullname):
    result = library.runner.get_result(context, 'last', group='tool')

    tests = library.process_nose_output(result.stderr)
    library.Assert.set_equal({fullname}, set(tests.keys()))


@given('a new repository is initialized')
def step_impl(context):
    library.runner.execute_command(context, 'git-init')


@given('all changes are committed')
def step_impl(context):
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
