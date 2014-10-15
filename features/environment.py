import sys

from steps.library import environment, runner
from quicktester.tests.clone import TemporaryClone


def __check_need_run(tag):
    if tag.startswith('require-python-version:') and sys.version_info.major != int(tag.rsplit(':', 1)[-1]):
        return False

    return True


def __mark_unrunnable(obj):
    if not all(__check_need_run(tag) for tag in obj.tags):
        obj.mark_skipped()


def before_feature(context, feature):
    __mark_unrunnable(feature)
    for scenario in feature.scenarios:
        __mark_unrunnable(scenario)


def before_scenario(context, scenario):
    context.environment = environment.RunEnvironment()
    context.environment.enter()

    runner.initialize_runner_context(context)


def after_scenario(context, scenario):
    context.environment.exit()
