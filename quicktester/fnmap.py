import collections
import re
import os.path


class FilenameMapping(object):
    def __init__(self, mappings):
        self.__mappings = collections.OrderedDict(mappings)

    def map(self, filename, variables=()):
        variables = dict(variables)
        filename = os.path.normpath(filename)

        for pattern, map_to in self.__mappings.items():
            pattern_replaced = self.__replace_variables(pattern, variables)

            if re.match(pattern_replaced, filename):
                filename = re.sub(
                    pattern_replaced,
                    self.__replace_variables(map_to, variables),
                    filename
                )
                break

        return os.path.normpath(filename)

    def __replace_variables(self, pattern, variables):
        res = pattern
        for variable, value in variables.items():
            res = res.replace('@{}@'.format(variable), value)

        return res


builtin_mappings = {
    'default': FilenameMapping(
        [
            (r'(.*/test_.*\.py)', r'\1'),
            (r'(.*)/.*\.py', r'\1'),
        ]
    ),

    'match': FilenameMapping(
        [
            (r'(.*/test_.*\.py)', r'\1'),
            (r'(.*)/(.*)\.py', r'\1/tests/test_\2.py'),
        ]
    ),

    'external': FilenameMapping(
        [
            (r'(@BASEPATH@/@TESTDIR@(?:.*/test_.*\.py))', r'\1'),
            (r'@BASEPATH@/[^/]+((?:/[^/]+)*/)(.*\.py)', r'@BASEPATH@/@TESTDIR@\1test_\2'),
        ]
    )
}
