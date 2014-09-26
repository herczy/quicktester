import os.path

from .module import Module, Package


class ModuleDiscovery(object):
    def __init__(self):
        self.__packages = []

    @property
    def packages(self):
        return iter(self.__packages)

    def discover_all(self, path):
        try:
            self.add_module_path(path)
            return

        except RuntimeError:
            pass

        if os.path.isdir(path):
            for sub in os.listdir(path):
                full = os.path.join(path, sub)

                try:
                    self.add_module_path(full)

                except RuntimeError:
                    pass

    def add_module_path(self, path):
        module = self.__get_module(path)
        if module is None:
            raise RuntimeError('{} is not a module nor a package'.format(path))

        self.__packages.append(module)

    def find_related_package(self, path, packages=None):
        if path.endswith('__init__.py'):
            path = os.path.dirname(path)

        path = os.path.abspath(path)
        if packages is None:
            packages = self.__packages

        for module in packages:
            if module.path == path:
                return module

            elif path.startswith(module.path):
                return self.find_related_package(path, packages=module.children)

        raise RuntimeError('Cannot find related package for {}'.format(path))

    @classmethod
    def __get_module(cls, path):
        if os.path.isfile(path):
            return Module.from_filename(path)

        elif os.path.isfile(os.path.join(path, '__init__.py')):
            pkg = Package.from_filename(path)

            for sub in os.listdir(path):
                if sub in {'__init__.py', '__init__.pyc'}:
                    continue

                full = os.path.join(path, sub)

                module = cls.__get_module(full)
                if module is not None:
                    pkg.add_child(module)

            return pkg
