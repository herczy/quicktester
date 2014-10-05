from steps.library import environment, runner
from quicktester.tests.clone import TemporaryClone


def before_scenario(context, scenario):
    context.environment = environment.RunEnvironment()
    context.environment.enter()

    runner.initialize_runner_context(context)


def after_scenario(context, scenario):
    context.environment.exit()
