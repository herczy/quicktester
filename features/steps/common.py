import os
import library


@given('an empty package "{package:w}"')
def step_impl(context, package):
    context.environment.write('{}/__init__.py'.format(package), '')
    context.environment.write('{}/tests/__init__.py'.format(package), '')


@given('the plugins are installed')
def step_impl(context):
    path = os.getcwd()

    context.environment.exit()
    try:
        library.build_egg_file(path)

    finally:
        context.environment.enter()


@when('the {kind:w} file "{filename}" is created')
@when('the {kind:w} file "{filename}" is changed')
@given('the {kind:w} file "{filename}" is created')
def step_impl(context, kind, filename):
    context.environment.write(filename, context.text)


@when('nose is run and {state:w}')
@when('nose is run again and {state:w}')
@when('nose is run again {count:d} times and {state:w} each time')
def step_impl(context, state, count=1):
    state = (state == 'passes')
    for _ in range(count):
        library.run_nose(expected_rc=(0 if state else 1))
