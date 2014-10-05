import library


@when('the CLI tool is executed')
def step_impl(context):
    context.cli_tool_stdout = library.run_quicktester_statistics()


@then('it does not print anything')
def step_impl(context):
    library.verify_context(context, 'cli_tool_stdout')

    library.Assert.equal('', context.cli_tool_stdout.strip())


@when('the CLI tool is executed with a backlog of {count:d}')
def step_impl(context, count):
    context.cli_tool_stdout = library.run_quicktester_statistics(cli_args='--backlog {}'.format(count))


@then('it prints the following')
def step_impl(context):
    library.verify_context(context, 'cli_tool_stdout')

    library.Assert.equal(context.text.rstrip(), context.cli_tool_stdout.rstrip())
