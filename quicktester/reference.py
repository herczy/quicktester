import sys
import os.path
import collections
import ast


def _default_import(pkg):
    __import__(pkg)
    return sys.modules[pkg]


class _ReferenceCollector(ast.NodeVisitor):
    def __init__(self):
        self.references = []

    def __add_aliases(self, level, base, aliases):
        for alias in aliases:
            fullname = base + tuple(alias.name.split('.'))
            self.references.append((level, fullname))

    def visit_ImportFrom(self, node):
        if node.module is None:
            basename = ()

        else:
            basename = tuple(node.module.split('.'))

        self.__add_aliases(node.level, basename, node.names)

    def visit_Import(self, node):
        self.__add_aliases(0, (), node.names)


class References(collections.Set):
    def __init__(self, ast, filename, cwd=None, _import=None):
        if cwd is None:
            cwd = '.'

        if _import is None:
            _import = _default_import

        self.__cwd = cwd
        self.__references = set()
        self.__import = _import

        self.__collect_references(ast, filename)

    def __collect_references(self, ast, filename):
        refcoll = _ReferenceCollector()
        refcoll.visit(ast)

        for level, fullname in refcoll.references:
            base = self.__get_module_from_filename(filename)

            try:
                package = self.__import('.'.join(base[:-level] + fullname))

            except ImportError:
                continue

            relname = os.path.relpath(package.__file__, self.__cwd)
            if relname.split(os.path.sep, 1)[0] == '..':
                continue

            self.__references.add(relname)

    def __get_module_from_filename(self, filename):
        filename, _ = os.path.splitext(filename)
        dirname, basename = os.path.split(filename)

        if dirname == '':
            return (basename,)

        return self.__get_module_from_filename(dirname) + (basename,)

    def __len__(self):
        return len(self.__references)

    def __iter__(self):
        return iter(self.__references)

    def __contains__(self, key):
        return key in self.__references
