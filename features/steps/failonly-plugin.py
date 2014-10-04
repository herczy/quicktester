import sys
import re
import library


@when('nose is run again with the failing tests and passes')
@when('nose is run again with the failing tests in the last {run_count:d} runs and passes')
def step_impl(context, run_count=1):
    context.nose_output = library.run_nose(cli_args='-v --run-count {}'.format(run_count))


@then('only the "{fullname}" tests has beed rerun')
def step_impl(context, fullname):
    tests = {}
    for line in context.nose_output.split('\n'):
        m = re.match(r'([a-zA-Z0-9_]+) \(([a-zA-Z0-9_\.]*)\) ... ([^\s]*)', line)
        if m is None:
            continue

        tests[m.group(2) + '.' + m.group(1)] = m.group(3)

    library.Assert.list_equal(list(tests.keys()), [fullname])
