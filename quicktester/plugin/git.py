from __future__ import print_function

import os.path
import nose
import sys

from ..git import Changes
from ..fnmap import builtin_mappings
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
        parser.add_option(
            '--filename-mapping',
            default='default',
            help='Specify the way git changes are mapped to the targets that ' +
                 'need to be run. There are two modes: \'default\', which expects ' +
                 'tests to be in the same structure as the packages and \'external\', ' +
                 'in which tests are under the tests/ directory. In the second case ' +
                 'the test for package.subpackage.module should be in ' +
                 'tests.package.subpackage.test_module'
        )

    def configure(self, options, config):
        if not options.git_changes:
            return

        if options.filename_mapping not in builtin_mappings:
            self._print_error('Unknown filename mapping \'{}\''.format(options.filename_mapping))
            exit(2)

        variables = {
            'BASEPATH': os.getcwd(),
            'TESTDIR': 'tests',
        }
        mapping = builtin_mappings[options.filename_mapping]

        self.enabled = True
        self.changes = frozenset(self.__get_relevant_changes(mapping, variables))

    def wantDirectory(self, path):
        if not any(util.is_reldir(change, path) or util.is_reldir(path, change) for change in self.changes):
            return False

    wantFile = wantDirectory

    def __get_relevant_changes(self, mapping, variables):
        for change in self._get_changes():
            yield mapping.map(os.path.abspath(change), variables)

    def _get_changes(self):
        return Changes()

    def _print_error(self, error):
        print(error, file=sys.stderr)
