from .assertfunc import Assert


def verify_context(context, attribute, msg=None):
    if msg is None:
        msg = 'The {!r} context attribute is missing'.format(attribute)

    Assert.true(hasattr(context, attribute), msg=msg)


def verify_environment(context):
    verify_context(
        context,
        'environment',
        msg='Somethings seriously wrong, the environment has not been initialized.\n' +
        'This task is the job of the features/environment.py script that is run by behave.'
    )
