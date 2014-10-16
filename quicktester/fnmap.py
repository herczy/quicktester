import os.path


class FilenameMapping(object):
    def map(self, filename, variables):
        raise NotImplementedError('{}.map'.format(type(self).__name__))


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
