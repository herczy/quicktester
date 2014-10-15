import unittest
import json
import tempfile
import mock

from . import PluginTestCase

from ..git import GitChangesPlugin


class TestGitChangesPlugin(PluginTestCase):
    changes = ()

    def plugin(self):
        return FakeGitChangesPlugin(self.changes)

    def test_disabled_by_default(self):
        plugin = self.get_configured_plugin('')

        self.assertFalse(plugin.enabled)

    def test_enabled_with_option(self):
        plugin = self.get_configured_plugin('--git-changes')

        self.assertTrue(plugin.enabled)

    def prepare_with_changes(self, changes, mapping='default'):
        self.changes = set(changes)
        plugin = self.get_configured_plugin('--git-changes --filename-mapping {}'.format(mapping))

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

    def test_alternative_filename_mapping(self):
        with mock.patch('os.getcwd') as getcwd:
            getcwd.return_value = '/path/to/quicktester'

            plugin = self.prepare_with_changes({'/path/to/quicktester/quicktester/module.py'}, mapping='external')

        self.assertEqual(None, plugin.wantDirectory('/path/to/quicktester/tests/test_module.py'))
        self.assertEqual(False, plugin.wantFile('/path/to/quicktester/tests/test_othermodule.py'))
        self.assertEqual(False, plugin.wantFile('/path/to/quicktester/quicktester/module.py'))


class FakeGitChangesPlugin(GitChangesPlugin):
    def __init__(self, changes):
        self.__changes = set(changes)

        super(FakeGitChangesPlugin, self).__init__()

    def _get_changes(self):
        return frozenset(self.__changes)
