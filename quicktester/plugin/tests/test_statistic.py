import tempfile

from . import PluginTestCase

from ..statistic import StatisticsPlugin
from ...statistic import Statistic
from ...tests.test_statistic import FakeResult, FakeTest
from .. import DEFAULT_STATISTICS_FILE


class StatisticsPluginTest(PluginTestCase):
    plugin = StatisticsPlugin

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

    def test_finalize_results(self):
        result = FakeResult([FakeTest('/path/to/module', 'module', 'Test.func')])
        result.errors.append(result.tests[0])

        with tempfile.NamedTemporaryFile(mode='w+') as f:
            f.write('[]')
            f.flush()

            plugin = self.get_configured_plugin('--statistics-file "{}"'.format(f.name))
            plugin.finalize(result)

            self.assertEqual(['/path/to/module'], Statistic(f.name).get_failure_paths(1))
