import os.path


def restrict(paths, restriction):
    return [path for path in paths if is_in_restricted(path, restriction)]


def is_in_restricted(path, restriction):
    for change in restriction:
        change_rel = os.path.relpath(path, change)
        if change_rel.split(os.path.sep, 1)[0] != '..':
            return True

    return False


def filter_non_test_paths(paths):
    res = []
    for path in paths:
        if os.path.isdir(path) or os.path.dirname(path).startswith('test_'):
            res.append(path)

        else:
            res.append(os.path.dirname(path))

    return res


def reduce_paths(paths):
    paths = list(paths)
    paths.sort()
    res = []

    for path in paths:
        if not res:
            res.append(path)
            continue

        if os.path.relpath(path, res[-1]).split(os.path.sep)[0] != '..':
            continue

        res.append(path)

    return res


def update_test_names(config, relevant_paths):
    if config.testNames:
        restricted = restrict(config.testNames, relevant_paths)
        if restricted:
            config.testNames = reduce_paths(restricted)

    else:
        config.testNames = reduce_paths(relevant_paths)
