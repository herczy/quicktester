import optparse
import unittest
import shlex

from ...tests import FakeConfig


class PluginTestCase(unittest.TestCase):
    plugin = None

    def process_plugin_options(self, cli, plugin=None):
        if plugin is None:
            plugin = self.plugin()

        parser = optparse.OptionParser()
        plugin.options(parser, {})
        return parser.parse_args(shlex.split(cli))[0]

    def get_configured_plugin(self, cli):
        plugin = self.plugin()
        ns = self.process_plugin_options(cli, plugin=plugin)
        plugin.configure(ns, FakeConfig())

        return plugin
