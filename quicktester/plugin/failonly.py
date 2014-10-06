import nose
import os.path

from ..statistic import Statistic
from .. import util

from . import DEFAULT_STATISTICS_FILE


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

        if not os.path.isfile(options.statistics_file):
            return

        self.run_count = options.run_count
        self.statistic = Statistic(options.statistics_file)
        self.failpaths = self.statistic.get_failure_paths(self.run_count)
        self.enabled = True

    def wantDirectory(self, path):
        if not any(util.is_reldir(fail, path) for fail in self.failpaths):
            return False

    def wantFunction(self, func):
        return self.check_if_failed(func)

    wantMethod = wantFunction
