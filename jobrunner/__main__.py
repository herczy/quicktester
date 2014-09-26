from __future__ import print_function

import argparse

from .runner import TestRunner
from .discovery import ModuleDiscovery
from .git import Changes


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-p', '--path', action='append',
                        help='List of paths to scan')

    command = parser.add_mutually_exclusive_group(required=True)
    command.add_argument('-c', '--changes', action='store_true',
                         help='List changed packages')
    command.add_argument('-RA', '--run-all', action='store_true',
                         help='Run all tests')
    command.add_argument('-RC', '--run-changed', action='store_true',
                         help='Run changed tests')

    options = parser.parse_args()

    discovery = ModuleDiscovery()
    paths = list(options.path or ('.',))

    for path in paths:
        discovery.discover_all(path)

    if options.changes:
        for filename, package in Changes.list_changed_packages(discovery):
            print(filename, '->', package.fqdn)

    elif options.run_all:
        return TestRunner(discovery.packages).run()

    elif options.run_changed:
        packages = [package for _, package in Changes.list_changed_packages(discovery)]
        return TestRunner(packages).run()


if __name__ == '__main__':
    exit(main())
