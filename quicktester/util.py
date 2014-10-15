import os.path


def is_reldir(path, base):
    return os.path.relpath(path, base).split(os.path.sep)[0] != '..'


def __is_testing_path(path, os_isdir_func):
    if os_isdir_func(path) or os.path.basename(path).startswith('test_'):
        return path

    else:
        return os.path.dirname(path)
