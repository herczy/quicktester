import collections
import re
import os.path


class FilenameMapping(object):
    def map(self, filename, variables):
        raise NotImplementedError('{}.map'.format(type(self).__name__))


class RegexMapping(FilenameMapping):
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


class DefaultMapping(FilenameMapping):
    def map(self, filename, variables=()):
        if not filename.endswith('.py'):
            return filename

        dirname, basename = os.path.split(filename)
        if basename.startswith('test_'):
            return filename

        return dirname


class NameMatchMapping(FilenameMapping):
    TEST_MODULE_PREFIX = 'test_'

    def map(self, filename, variables=()):
        if not filename.endswith('.py'):
            return filename

        dirname, basename = os.path.split(filename)
        if basename.startswith(self.TEST_MODULE_PREFIX):
            return filename

        return os.path.join(dirname, 'tests', self.TEST_MODULE_PREFIX + basename)


class ExternalNameMapping(FilenameMapping):
    def map(self, filename, variables=()):
        variables = dict(variables)
        basepath = variables['BASEPATH']
        tests = variables['TESTDIR']

        if not filename.endswith('.py'):
            return filename

        dirname, basename = os.path.split(filename)
        if basename.startswith(NameMatchMapping.TEST_MODULE_PREFIX):
            return filename

        testmodule = os.path.relpath(dirname, basepath).split(os.path.sep)[1:]
        testmodule.append(NameMatchMapping.TEST_MODULE_PREFIX + basename)
        return os.path.join(basepath, tests, *testmodule)


builtin_mappings = {
    'default': DefaultMapping(),
    'match': NameMatchMapping(),
    'external': ExternalNameMapping()
}
