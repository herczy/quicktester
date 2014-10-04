import unittest
import json
import tempfile

from . import PluginTestCase

from ..failonly import FailOnlyPlugin
from ...statistic import Statistic
from ...tests.test_statistic import FakeResult, FakeTest
from ...tests import FakeConfig
from .. import DEFAULT_STATISTICS_FILE


class FailOnlyPluginTest(PluginTestCase):
    plugin = FailOnlyPlugin

    def test_disabled_by_default(self):
        plugin = self.get_configured_plugin('')

        self.assertFalse(plugin.enabled)

    def test_disabled_without_statistics_file(self):
        plugin = self.get_configured_plugin('--run-count 1')

        self.assertFalse(plugin.enabled)

    def test_disabled_with_nonexistent_statistics_file(self):
        plugin = self.get_configured_plugin('--run-count 1', statistics_file='/path/does/not/exist')

        self.assertFalse(plugin.enabled)

    def setup_plugin(self, backlog=1, content=None, config=None):
        if content is None:
            content = [[["/path/to/module", "module", "Test.func"]]]

        with tempfile.NamedTemporaryFile(mode='w+') as f:
            json.dump(content, f)
            f.flush()

            return self.get_configured_plugin('--run-count {}'.format(backlog), config=config, statistics_file=f.name)

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
