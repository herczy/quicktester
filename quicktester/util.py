import os.path


def restrict(paths, restriction):
    return [path for path in paths if is_in_restricted(path, restriction)]


def is_in_restricted(path, restriction):
    for change in restriction:
        change_rel = os.path.relpath(path, change)
        if change_rel.split(os.path.sep, 1)[0] != '..':
            return True

    return False
