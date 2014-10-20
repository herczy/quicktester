import argparse
import nose

from ..statistic import Report, Statistic

from . import DEFAULT_STATISTICS_FILE


class StatisticsPlugin(nose.plugins.Plugin):
    '''Collect result statistics about the plugin run.'''

    name = 'statistics'
    statfile = None
    statreport = None

    def options(self, parser, env):
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
        if options.disable_statistics:
            self.enabled = False
            return

        self.enabled = True
        self.statfile = options.statistics_file
        self.statreport = Report()

    def addSuccess(self, case):
        self.statreport.add(case, Report.STATUS_PASSED)

    def addFailure(self, case, error):
        self.statreport.add(case, Report.STATUS_FAILED)

    def addError(self, case, error):
        self.statreport.add(case, Report.STATUS_ERROR)

    def addSkip(self, case):
        self.statreport.add(case, Report.STATUS_SKIPPED)

    def finalize(self, result):
        self._get_statistics(self.statfile).report_run(self.statreport)

    def _get_statistics(self, filename):
        return Statistic(filename)


def quicktester_statistics():
    parser = argparse.ArgumentParser(
        description='Statistic analizer for the quicktester nose plugins'
    )

    parser.add_argument('-f', '--file', default=DEFAULT_STATISTICS_FILE,
                        help='Statistics file (default: %(default)s)')
    parser.add_argument('-b', '--backlog', default=10, type=int,
                        help='Backlog to show (default: %(default)s)')
    parser.add_argument('-a', '--show-all-tests', action='store_true', default=False,
                        help='Show statistics for all tests collected')
    parser.add_argument('-F', '--only-failing', action='store_true', default=False,
                        help='Show only tests that had a failure in the runs shown')

    options = parser.parse_args()

    Statistic(options.file).dump_info(
        options.backlog,
        dump_all=options.show_all_tests,
        failonly=options.only_failing
    )
    return 0
