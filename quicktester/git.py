import subprocess
import collections


class GitError(Exception):
    def __init__(self, message, returncode, stderr):
        super(GitError, self).__init__(message)

        self.returncode = returncode
        self.stderr = stderr


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
        process = subprocess.Popen(['git', 'status', '--porcelain'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise GitError('git status command failed', process.returncode, stderr)

        return stdout.decode()
