import nose
import subprocess
import os.path

from ..statistic import Statistic
from ..git import Changes
from .. import util


DEFAULT_STATISTICS_FILE = '.quicktester-statistics'


class GitChanges(nose.plugins.Plugin):
    name = 'git-change'
    enabled = False

    def options(self, parser, env):
        parser.add_option(
            '--git-changes',
            action='store_true',
            help='Run only modules where git changed'
        )

    def prepareLoader(self, loader):
        self.loader = loader

    def configure(self, options, config):
        if not options.git_changes:
            return

        self.enabled = True
        changes = Changes()
        if not changes:
            raise RuntimeError('No GIT changes found')

        util.update_test_names(config, changes)
