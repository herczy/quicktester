import os.path
import nose

from ..git import Changes
from ..reference import References
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
        self.changes = util.get_testing_paths(self.__get_relevant_changes())
        self.selector = None
        self.refs = {}

    def prepareTestLoader(self, loader):
        self.selector = loader.selector
        for path, refs in self._get_references('.', nose.selector.Selector(None)):
            print(path, refs)

    def wantDirectory(self, path):
        if not any(util.is_reldir(change, path) or util.is_reldir(path, change) for change in self.changes):
            return False

    wantFile = wantDirectory

    def __get_relevant_changes(self):
        return [change for change in self._get_changes() if change.endswith('.py') or os.path.isdir(change)]

    def _get_changes(self):
        return Changes()

    def _get_references(self, path, selector):
        for sub in os.listdir(path):
            full = os.path.join(path, sub)
            if os.path.isdir(full) and selector.wantDirectory(full):
                yield from self._get_references(full, selector)

            elif os.path.isfile(full) and selector.wantFile(full):
                yield self._get_references_from_file(full)

    def _get_references_from_file(self, path):
        return (path, set(References.load_from_file(path)))
