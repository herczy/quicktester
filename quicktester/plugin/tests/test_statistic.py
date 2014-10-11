import unittest
import os.path
import tempfile

from . import PluginTestCase, FakeDatabaseFactory

from ..statistic import StatisticsPlugin
from ...statistic import Report, Statistic
from ...tests.test_statistic import FakeResult, FakeTest, FakeDatabase, TemporaryStatisticsFile
from .. import DEFAULT_STATISTICS_FILE


class StatisticsPluginTest(PluginTestCase):
    def plugin(self):
        return FakeStatisticsPlugin()

    def test_enabled_by_default(self):
        plugin = self.get_configured_plugin('')

        self.assertTrue(plugin.enabled)
        self.assertEqual(DEFAULT_STATISTICS_FILE, plugin.statfile)

    def test_disable_plugin(self):
        plugin = self.get_configured_plugin('--disable-statistic')

        self.assertFalse(plugin.enabled)
        self.assertEqual(None, plugin.statfile)

    def test_set_statfile(self):
        plugin = self.get_configured_plugin('--statistics-file testfile')

        self.assertEqual('testfile', plugin.statfile)

    def assert_reported(self, expected_status, callname, *extra):
        test = FakeTest('', '', '')

        plugin = self.get_configured_plugin('')
        getattr(plugin, callname)(test, *extra)

        self.assertListEqual([(test, expected_status)], list(plugin.statreport))

    def test_add_success(self):
        self.assert_reported(Report.STATUS_PASSED, 'addSuccess')

    def test_add_failure(self):
        self.assert_reported(Report.STATUS_FAILED, 'addFailure', '')

    def test_add_error(self):
        self.assert_reported(Report.STATUS_ERROR, 'addError', '')

    def test_add_skip(self):
        self.assert_reported(Report.STATUS_SKIPPED, 'addSkip')

    def test_finalize_results(self):
        test = FakeTest('/path/to/module', 'module', 'Test.func')

        filename = 'statfilename'
        plugin = self.get_configured_plugin('--statistics-file "{}"'.format(filename))
        plugin.addError(test, '')
        plugin.finalize(None)

        self.assertEqual(
            {'/path/to/module'},
            plugin._get_statistics(filename).get_failure_paths(1)
        )


class FakeStatisticsPlugin(StatisticsPlugin):
    statistics_files = {}

    def _get_statistics(self, filename):
        if filename not in self.statistics_files:
            self.statistics_files[filename] = Statistic(
                filename,
                dbfactory=FakeDatabaseFactory(
                    filename,
                    FakeDatabase()
                )
            )

        return self.statistics_files[filename]
