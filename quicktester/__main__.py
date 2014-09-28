from __future__ import print_function

import argparse

from .runner import TestRunner, RunnerConfig
from .discovery import ModuleDiscovery
from .git import Changes


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--path', action='append',
                        help='List of paths to scan')
    parser.add_argument('-v', dest='verbosity', action='count', default=0,
                        help='Test run verbosity (default: summary only)')
    parser.add_argument('--stop', dest='stop', action='store_true', default=False,
                        help='Stop if an error is encountered')

    command = parser.add_mutually_exclusive_group(required=True)
    command.add_argument('-a', '--run-all', action='store_true',
                         help='Run all tests')
    command.add_argument('-c', '--run-changed', action='store_true',
                         help='Run changed tests')
    command.add_argument('-f', '--run-failed', type=int, metavar='RUNCOUNT', default=None,
                         help='Rerun tests that failied in the last few runs (default: %(default)s)')

    options = parser.parse_args()

    discovery = ModuleDiscovery()
    paths = list(options.path or ('.',))

    for path in paths:
        discovery.discover_all(path)

    config = RunnerConfig(
        verbosity=options.verbosity,
        stop_on_error=options.stop,
        run_only_failed=options.run_failed,
    )

    if options.run_all or options.run_failed is not None:
        packages = discovery.packages

    elif options.run_changed:
        packages = [package for _, package in Changes.list_changed_packages(discovery)]

    return TestRunner(packages, config).run()


if __name__ == '__main__':
    exit(main())