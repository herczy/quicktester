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

    options = parser.parse_args()

    discovery = ModuleDiscovery()
    paths = list(options.path or ('.',))

    for path in paths:
        discovery.discover_all(path)

    if options.run_all:
        packages = discovery.packages

    elif options.run_changed:
        changes = list(Changes.list_changed_packages(discovery))
        packages = [package for _, package in changes]

    config = RunnerConfig(
        verbosity=options.verbosity,
        stop_on_error=options.stop
    )
    testrunner = TestRunner(packages, config)

    return testrunner.run()


if __name__ == '__main__':
    exit(main())
