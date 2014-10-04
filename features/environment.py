from steps import library
from quicktester.tests.clone import TemporaryClone


def before_scenario(context, scenario):
    context.git_repo = TemporaryClone()
    context.git_repo.__enter__()


def after_scenario(context, scenario):
    context.git_repo.__exit__(None, None, None)
