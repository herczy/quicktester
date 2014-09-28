import sys
import os.path
import subprocess

from . import util


class Changes(object):
    __failed = False

    def __init__(self):
        self.__changed = set()

        self.__collect_changes()

    def restrict_paths(self, paths):
        '''Restrict the given paths to the changes.'''

        if self.__failed:
            return paths

        return util.restrict(paths, self.__changed)

    def get_changes(self):
        if self.__failed:
            return []

        return list(self.__changed)

    def __collect_changes(self):
        try:
            res = subprocess.check_output(['git', 'status', '--porcelain']).decode()

        except subprocess.CalledProcessError:
            self.__failed = True
            print('Warning: no git changes could be found', file=sys.stderr)
            return

        for line in res.split('\n'):
            line = line.strip()
            if not line:
                continue

            filename = line[3:]
            if not filename.endswith('.py'):
                continue

            self.__changed.add(os.path.abspath(filename))
