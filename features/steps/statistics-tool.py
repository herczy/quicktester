import library
from quicktester.tests.clone import TemporaryClone


@given('a freshly-cloned git repository with some tests')
def step_impl(context):
    pass


@when('the CLI tool is executed')
def step_impl(context):
    context.cli_tool_stdout = library.run_quicktester_statistics()


@then('it does not print anything')
def step_impl(context):
    library.Assert.equal('', context.cli_tool_stdout.strip())


@given('the plugins are accessible')
def step_impl(context):
    library.ensure_plugins()


@when('the test file "{filename}" is created')
@when('the test file "{filename}" is changed')
def step_impl(context, filename):
    context.git_repo.write(filename, context.text)


@when('nose is run and {state:w}')
@when('nose is run again and {state:w}')
def step_impl(context, state):
    state = (state == 'passes')
    library.run_nose(expected_rc=(0 if state else 1))


@when('the CLI tool is executed with a backlog of {count:d}')
def step_impl(context, count):
    context.cli_tool_stdout = library.run_quicktester_statistics(cli_args='--backlog {}'.format(count))


@then('it prints the following')
def step_impl(context):
    library.Assert.equal(context.text.rstrip(), context.cli_tool_stdout.rstrip())
