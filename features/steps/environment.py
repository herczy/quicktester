import tempfile
import atexit
import shutil
import os.path
import errno


class RunEnvironment(object):
    __cleanup_directories = set()

    @classmethod
    def mkdtemp(cls, *args, **kwargs):
        path = tempfile.mkdtemp(*args, **kwargs)
        cls.__cleanup_directories.add(path)

        return path

    @classmethod
    def rmdtemp(cls, path):
        shutil.rmtree(path, ignore_errors=True)

        if path in cls.__cleanup_directories:
            cls.__cleanup_directories.remove(path)

    @classmethod
    def cleanup(cls):
        for path in set(cls.__cleanup_directories):
            cls.rmdtemp(path)

    def __init__(self):
        self.__directory = self.mkdtemp(prefix='quicktester-behave-')
        self.__working_dir = os.getcwd()

    def __del__(self):
        self.rmdtemp(self.__directory)

    def enter(self):
        os.chdir(self.__directory)

    def exit(self):
        os.chdir(self.__working_dir)

    def get_path(self, path):
        return os.path.join(self.__directory, path)

    def makedirs(self, path, exist_ok=False, raw_path=False):
        if not raw_path:
            path = self.get_path(path)

        try:
            os.makedirs(self.get_path(path))

        except OSError as exc:
            if not exist_ok or exc.errno != errno.EEXIST or not os.path.isdir(path):
                raise

    def write(self, path, content):
        path = self.get_path(path)

        self.makedirs(os.path.dirname(path), exist_ok=True, raw_path=True)
        with open(path, 'w') as f:
            f.write(content)

    def read(self, path):
        with open(self.get_path(path)) as f:
            return f.read()

atexit.register(RunEnvironment.cleanup)
