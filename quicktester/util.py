import os.path


def is_reldir(path, base):
    return os.path.relpath(path, base).split(os.path.sep)[0] != '..'


def __is_testing_path(path, os_isdir_func):
    if os_isdir_func(path) or os.path.basename(path).startswith('test_'):
        return path

    else:
        return os.path.dirname(path)


def is_in_restricted(path, restriction):
    return any(is_reldir(path, change) for change in restriction)


def restrict(paths, restriction):
    return [path for path in paths if is_in_restricted(path, restriction)]


def get_testing_paths(paths, os_isdir_func=os.path.isdir):
    return [__is_testing_path(path, os_isdir_func=os_isdir_func) for path in paths]


def reduce_paths(paths):
    res = []
    for path in sorted(paths):
        if res and is_reldir(path, res[-1]):
            continue

        res.append(path)

    return res


def update_test_names(config, relevant_paths):
    if not config.testNames:
        config.testNames = list(relevant_paths)
        return

    restricted = restrict(config.testNames, relevant_paths)
    if restricted:
        config.testNames = reduce_paths(restricted)
