import library


@given('a new repository is initialized')
def step_impl(context):
    library.init_git_repo()


@given('all changes are committed')
def step_impl(context):
    library.commit_everything()


@when('nose is run for the git changes')
def step_impl(context):
    context.nose_output = library.run_nose(cli_args='-v --git-changes', expected_rc=None)


@then('no tests are run')
def step_impl(context):
    library.verify_context(context, 'nose_output')

    tests = library.process_nose_output(context.nose_output)
    library.Assert.list_equal([], list(tests.keys()))


@then('the following tests are run')
def step_impl(context):
    library.verify_context(context, 'nose_output')

    tests = library.process_nose_output(context.nose_output)
    library.Assert.set_equal(
        set(context.text.split('\n')),
        set(tests.keys())
    )
