from steps import environment
from quicktester.tests.clone import TemporaryClone


def before_scenario(context, scenario):
    context.environment = environment.RunEnvironment()
    context.environment.enter()


def after_scenario(context, scenario):
    context.environment.exit()
