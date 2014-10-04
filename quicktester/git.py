import subprocess
import collections


class GitError(Exception):
    pass


class Changes(collections.Set):
    def __init__(self, git_status_func=None):
        if git_status_func is None:
            git_status_func = self.__git_status

        self.__changes = frozenset(self.__get_changes(git_status_func))

        super(Changes, self).__init__()

    def __len__(self):
        return len(self.__changes)

    def __contains__(self, item):
        return item in self.__changes

    def __iter__(self):
        return iter(self.__changes)

    def __get_changes(self, git_status_func):
        for line in git_status_func().split('\n'):
            if line:
                yield line[3:]

    def __git_status(self):
        try:
            return subprocess.check_output(['git', 'status', '--porcelain']).decode()

        except subprocess.CalledProcessError as exc:
            raise GitError(str(exc))
