import sys
import re
import library


@when('nose is run again with the failing tests and passes')
@when('nose is run again with the failing tests in the last {run_count:d} runs and passes')
def step_impl(context, run_count=1):
    context.nose_output = library.run_nose(cli_args='-v --run-count {}'.format(run_count))


@then('only the "{fullname}" tests has beed rerun')
def step_impl(context, fullname):
    tests = library.process_nose_output(context.nose_output)
    library.Assert.list_equal([fullname], list(tests.keys()))
