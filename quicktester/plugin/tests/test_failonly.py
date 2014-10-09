import unittest
import json
import tempfile

from . import PluginTestCase, FakeDatabaseFactory

from ..failonly import FailOnlyPlugin
from ...statistic import Statistic
from ...tests.test_statistic import FakeResult, FakeTest, TemporaryStatisticsFile, FakeDatabase
from ...tests import FakeConfig
from .. import DEFAULT_STATISTICS_FILE


class FailOnlyPluginTest(PluginTestCase):
    plugin = FailOnlyPlugin

    def setUp(self):
        self.statistics = Statistic(
            DEFAULT_STATISTICS_FILE,
            dbfactory=FakeDatabaseFactory(DEFAULT_STATISTICS_FILE, FakeDatabase())
        )

    def plugin(self):
        return FakeFailOnlyPlugin(self.statistics)

    def test_disabled_by_default(self):
        plugin = self.get_configured_plugin('')

        self.assertFalse(plugin.enabled)

    def test_disabled_without_statistics_file(self):
        plugin = self.get_configured_plugin('--run-count 1')

        self.assertFalse(plugin.enabled)

    def test_disabled_with_nonexistent_statistics_file(self):
        plugin = self.get_configured_plugin('--run-count 1', statistics_file='/path/does/not/exist')

        self.assertFalse(plugin.enabled)

    def setup_plugin(self):
        result = FakeResult([FakeTest("/path/to/module", "module", "Test.func")])
        result.failures.append((result.tests[0], ''))
        self.statistics.report_result(result)

        return self.get_configured_plugin('--run-count 1', statistics_file=DEFAULT_STATISTICS_FILE)

    def test_enabled_with_existing_statistics_file(self):
        plugin = self.setup_plugin()

        self.assertTrue(plugin.enabled)
        self.assertEqual(1, plugin.run_count)

    def test_want_directory(self):
        plugin = self.setup_plugin()

        self.assertEqual(False, plugin.wantDirectory('/path/irrelevant'))
        self.assertEqual(None, plugin.wantDirectory('/path'))
        self.assertEqual(None, plugin.wantDirectory('/path/to'))

    def test_want_module_and_function(self):
        fake0 = FakeTest('/path/to/module', 'module', 'Test.func')
        fake1 = FakeTest('/path/to/module2', 'module', 'Test.func2')

        plugin = self.setup_plugin()

        self.assertEqual(True, plugin.wantFunction(fake0))
        self.assertEqual(False, plugin.wantFunction(fake1))

        self.assertEqual(True, plugin.wantMethod(fake0))
        self.assertEqual(False, plugin.wantMethod(fake1))


class FakeFailOnlyPlugin(FailOnlyPlugin):
    def __init__(self, statistics):
        self.__statistics = statistics

    def _get_statistics(self, filename):
        assert filename == DEFAULT_STATISTICS_FILE
        return self.__statistics

    def _os_isfile(self, filename):
        return filename == DEFAULT_STATISTICS_FILE
