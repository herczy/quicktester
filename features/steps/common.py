import library


@given('a freshly-cloned git repository with some tests')
def step_impl(context):
    pass


@given('the plugins are accessible')
def step_impl(context):
    library.ensure_plugins()


@when('the test file "{filename}" is created')
@when('the test file "{filename}" is changed')
def step_impl(context, filename):
    context.git_repo.write(filename, context.text)


@when('nose is run and {state:w}')
@when('nose is run again and {state:w}')
@when('nose is run again {count:d} times and {state:w} each time')
def step_impl(context, state, count=1):
    state = (state == 'passes')
    for _ in range(count):
        library.run_nose(expected_rc=(0 if state else 1))
