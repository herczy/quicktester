import argparse
import nose

from ..statistic import Statistic

from . import DEFAULT_STATISTICS_FILE


class StatisticsPlugin(nose.plugins.Plugin):
    '''Collect result statistics about the plugin run.'''

    name = 'statistics'
    statfile = None

    def options(self, parser, env):
        super(StatisticsPlugin, self).options(parser, env)

        parser.add_option(
            '--disable-statistics',
            default=False,
            action='store_true',
            help='Disable collecting statistics'
        )
        parser.add_option(
            '--statistics-file',
            default=DEFAULT_STATISTICS_FILE,
            help='Statistics filename'
        )

    def configure(self, options, config):
        super(StatisticsPlugin, self).configure(options, config)

        if options.disable_statistics:
            self.enabled = False
            return

        self.enabled = True
        self.statfile = options.statistics_file

    def finalize(self, result):
        Statistic(self.statfile).report_result(result)


def quicktester_statistics():
    parser = argparse.ArgumentParser(
        description='Statistic analizer for the quicktester nose plugins'
    )

    parser.add_argument('-f', '--file', default=DEFAULT_STATISTICS_FILE,
                        help='Statistics file (default: %(default)s')
    parser.add_argument('-b', '--backlog', default=10,
                        help='Backlog to show (default: %(default)s')

    options = parser.parse_args()

    Statistic(options.file).dump_info(options.backlog)
    return 0
