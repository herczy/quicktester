import os.path
import nose

from ..git import Changes
from .. import util


class GitChangesPlugin(nose.plugins.Plugin):
    name = 'git-change'
    enabled = False
    changes = None

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
        self.changes = util.get_testing_paths(self._get_changes())

    def wantDirectory(self, path):
        if not any(util.is_reldir(change, path) or util.is_reldir(path, change) for change in self.changes):
            return False

    wantFile = wantDirectory

    def _get_changes(self):
        return Changes()
