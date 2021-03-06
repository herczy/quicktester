import unittest
import json
import tempfile
import mock

from . import PluginTestCase

from ..git import GitChangesPlugin
from ...git import GitError


class TestGitChangesPlugin(PluginTestCase):
    changes = ()
    raise_error = None

    def plugin(self):
        self.error = None
        def _set_error(error):
            self.error = error

        return FakeGitChangesPlugin(self.changes, _set_error, self.raise_error)

    def test_disabled_by_default(self):
        plugin = self.get_configured_plugin('')

        self.assertFalse(plugin.enabled)

    def test_enabled_with_option(self):
        plugin = self.get_configured_plugin('--git-changes')

        self.assertTrue(plugin.enabled)

    def prepare_with_changes(self, changes, extra_options='', raise_error=None):
        self.changes = set(changes)
        self.raise_error = raise_error
        plugin = self.get_configured_plugin('--git-changes {}'.format(extra_options))

        return plugin

    def test_want_directory_if_testfile_changed(self):
        plugin = self.prepare_with_changes({'quicktester/plugin/tests/test_git.py'})

        self.assertEqual(None, plugin.wantDirectory('quicktester/plugin/tests'))
        self.assertEqual(None, plugin.wantDirectory('quicktester'))
        self.assertEqual(False, plugin.wantDirectory('quicktester/tests'))

    def test_want_directory_if_module_changed(self):
        plugin = self.prepare_with_changes({'quicktester/plugin/git.py'})

        self.assertEqual(None, plugin.wantDirectory('quicktester/plugin/tests'))
        self.assertEqual(None, plugin.wantDirectory('quicktester/plugin'))
        self.assertEqual(None, plugin.wantDirectory('quicktester'))
        self.assertEqual(False, plugin.wantDirectory('quicktester/tests'))

    def test_want_file_if_testfile_changed(self):
        plugin = self.prepare_with_changes({'quicktester/plugin/tests/test_git.py'})

        self.assertEqual(None, plugin.wantFile('quicktester/plugin/tests/test_git.py'))
        self.assertEqual(False, plugin.wantFile('quicktester/plugin/tests/test_statistics.py'))

    def test_want_file_if_module_changed(self):
        plugin = self.prepare_with_changes({'quicktester/plugin/git.py'})

        self.assertEqual(None, plugin.wantFile('quicktester/plugin/tests/test_statistic.py'))
        self.assertEqual(False, plugin.wantFile('quicktester/tests/test_statistic.py'))

    def test_ignore_non_python_files_or_directories(self):
        plugin = self.prepare_with_changes({'junk.txt', 'quicktester/tests'})

        self.assertEqual(None, plugin.wantDirectory('quicktester'))
        self.assertEqual(None, plugin.wantDirectory('quicktester/tests'))
        self.assertEqual(None, plugin.wantFile('quicktester/tests/test_git.py'))
        self.assertEqual(False, plugin.wantFile('quicktester/test_git.py'))

    def test_external_filename_mapping(self):
        with mock.patch('os.getcwd') as getcwd:
            getcwd.return_value = '/path/to/quicktester'

            plugin = self.prepare_with_changes({'/path/to/quicktester/quicktester/module.py'}, extra_options='--separate-tests tests')

        self.assertEqual(None, plugin.wantDirectory('/path/to/quicktester/tests/test_module.py'))
        self.assertEqual(False, plugin.wantFile('/path/to/quicktester/tests/test_othermodule.py'))
        self.assertEqual(False, plugin.wantFile('/path/to/quicktester/quicktester/module.py'))

    def test_match_filename_mapping(self):
        plugin = self.prepare_with_changes({'/path/to/quicktester/quicktester/module.py'}, extra_options='--match-names')

        self.assertEqual(None, plugin.wantDirectory('/path/to/quicktester/quicktester/tests/test_module.py'))
        self.assertEqual(False, plugin.wantDirectory('/path/to/quicktester/quicktester/tests/test_module2.py'))
        self.assertEqual(False, plugin.wantFile('/path/to/quicktester/quicktester/module.py'))

    def test_specify_mutually_exclusive(self):
        self.prepare_with_changes({}, extra_options='--separate-tests x --match-names')

        self.assertNotEqual(None, self.error)

    def test_not_a_git_directory(self):
        plugin = self.prepare_with_changes(
            {},
            raise_error=GitError(
                'Not a git repository',
                'fatal: Not a git repository (or any of the parent directories): .git\n',
                128
            )
        )

        self.assertFalse(plugin.enabled)


class FakeGitChangesPlugin(GitChangesPlugin):
    def __init__(self, changes, error_func, raise_error):
        self.__changes = set(changes)
        self.error_func = error_func
        self.raise_error = raise_error

        super(FakeGitChangesPlugin, self).__init__()

    def _get_changes(self):
        if self.raise_error is not None:
            raise self.raise_error

        return frozenset(self.__changes)

    def _parser_error(self, error):
        self.error_func(error)
