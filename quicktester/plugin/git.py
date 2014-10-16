from __future__ import print_function

import os.path
import nose
import sys

from ..git import Changes, GitError
from ..fnmap import DefaultMapping, NameMatchMapping, ExternalNameMapping
from .. import util


class GitChangesPlugin(nose.plugins.Plugin):
    name = 'git-change'
    enabled = False
    changes = None
    parser = None

    def options(self, parser, env):
        parser.add_option(
            '--git-changes',
            action='store_true',
            help='Run only modules where git changed'
        )
        parser.add_option(
            '--separate-tests',
            metavar='TESTPATH',
            help='If given, the tests will be assumed to be in the given directory.'
        )
        parser.add_option(
            '--match-names',
            action='store_true',
            help='If set, the plugin will try to match module names with test module names. ' +
                 'I.e. changes in package.module will cause the package.tests.test_module to rerun.'
        )
        self.parser = parser

    def configure(self, options, config):
        if not options.git_changes:
            return

        if options.separate_tests and options.match_names:
            self._parser_error('--separate-tests and --match-names are mutually exclusive')

        try:
            changes = self._get_changes()

        except GitError as exc:
            return

        if options.separate_tests:
            mapping = ExternalNameMapping()

        elif options.match_names:
            mapping = NameMatchMapping()

        else:
            mapping = DefaultMapping()

        self.enabled = True
        self.changes = frozenset(self.__get_relevant_changes(changes, mapping))

    def wantDirectory(self, path):
        if not any(util.is_reldir(change, path) or util.is_reldir(path, change) for change in self.changes):
            return False

    wantFile = wantDirectory

    def __get_relevant_changes(self, changes, mapping):
        for change in changes:
            yield mapping.map(os.path.abspath(change))

    def _get_changes(self):
        return Changes()

    def _parser_error(self, error):
        self.parser.error(error)
