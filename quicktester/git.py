import subprocess


class Changes(object):
    def __init__(self):
        self.__changed = []
        self.__collect_changes()

    @property
    def changes(self):
        return iter(self.__changed)

    def __collect_changes(self):
        try:
            res = subprocess.check_output(['git', 'status', '--porcelain']).decode()

        except subprocess.CalledProcessError:
            return

        for line in res.split('\n'):
            index, filename = line[:2], line[3:]
            self.__changed.append(filename)

    @classmethod
    def list_changed_packages(cls, discovery):
        for filename in cls().changes:
            try:
                yield filename, discovery.find_related_package(filename)

            except RuntimeError:
                continue
