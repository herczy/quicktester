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

    def get_configured_plugin(self, cli, config=None, **extra):
        plugin = self.plugin()
        ns = self.process_plugin_options(cli, plugin=plugin)
        for key, value in extra.items():
            setattr(ns, key, value)

        if config is None:
            config = FakeConfig()

        plugin.configure(ns, config)

        return plugin


class FakeDatabaseFactory(object):
    def __init__(self, expected_filename, db):
        self.expected_filename = expected_filename
        self.db = db

    def init_connection(self, filename):
        assert self.expected_filename == filename
        return self.db
