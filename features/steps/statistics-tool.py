import library
from quicktester.tests.clone import TemporaryClone


@given('a freshly-cloned git repository with some tests')
def step_impl(context):
    context.git_repo = TemporaryClone()


@when('the CLI tool is executed')
def step_impl(context):
    with context.git_repo as repo:
        context.stdout = library.run_quicktester_statistics()


@then('it does not print anything')
def step_impl(context):
    library.Assert.equal('', context.stdout.strip())
