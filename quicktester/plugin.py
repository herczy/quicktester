import nose
import subprocess
import os.path

from .statistic import Statistic, DEFAULT_STATISTICS_FILE
from .git import Changes
from . import util


class StatisticsPlugin(nose.plugins.Plugin):
    '''Collect result statistics about the plugin run.'''

    name = 'statistics'
    statfile = None

    def options(self, parser, env):
        super(StatisticsPlugin, self).options(parser, env)

        parser.add_option(
            '--disable-statistics',
            default=False,
            action='store_true',
            help='Disable collecting statistics'
        )
        parser.add_option(
            '--statistics-file',
            default=DEFAULT_STATISTICS_FILE,
            help='Statistics filename'
        )

    def configure(self, options, config):
        super(StatisticsPlugin, self).configure(options, config)

        if options.disable_statistics:
            self.enabled = False
            return

        self.enabled = True
        self.statfile = options.statistics_file

    def finalize(self, result):
        Statistic(self.statfile).report_result(result)


class FailOnlyPlugin(nose.plugins.Plugin):
    '''Run only tests that have failed previously.'''

    name = 'fail-only'
    run_count = 0
    statistic = None

    def check_if_failed(self, obj):
        return self.statistic.check_if_failed(obj, self.run_count)

    #
    # Interface functions
    #
    def options(self, parser, env):
        super(FailOnlyPlugin, self).options(parser, env)

        parser.add_option(
            '--run-count',
            default=0,
            type=int,
            metavar='COUNT',
            help='Number of runs to take into account'
        )

    def configure(self, options, config):
        super(FailOnlyPlugin, self).configure(options, config)

        if options.run_count <= 0 or getattr(options, 'statistics_file', None) is None:
            return

        self.run_count = options.run_count
        self.statistic = Statistic(options.statistics_file)
        self.enabled = True

        failed_paths = self.statistic.get_failure_paths(self.run_count)
        if not config.testNames and failed_paths:
            config.testNames = failed_paths

    def wantFunction(self, func):
        return self.check_if_failed(func)

    def wantMethod(self, method):
        return self.check_if_failed(method)


class GitChanges(nose.plugins.Plugin):
    name = 'git-change'
    enabled = False
    changes = ()

    def options(self, parser, env):
        parser.add_option(
            '--git-changes',
            action='store_true',
            help='Run only modules where git changed'
        )

    def configure(self, options, config):
        if not options.git_changes:
            return

        self.enabled = True
        if config.testNames:
            config.testNames = Changes().restrict_paths(config.testNames)

        else:
            config.testNames = Changes().get_changes()
