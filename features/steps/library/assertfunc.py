import re
import os.path
import unittest


def __make_assert_class():
    caps = re.compile('([A-Z])')
    prefix = 'assert_'

    def make_pep8_name(name):
        sub = caps.sub(lambda m: '_' + m.groups()[0].lower(), name)
        return sub[len(prefix):]

    def make_caller(obj, name):
        def func(cls, *args, **kwargs):
            return getattr(obj, name)(*args, **kwargs)

        return classmethod(func)

    class Dummy(unittest.TestCase):
        def nop():
            pass

    assert_dict = {}
    dummy = Dummy('nop')
    dummy.maxDiff = None
    for attribute in dir(dummy):
        if not attribute.startswith('assert') or '_' in attribute:
            continue

        pep8_name = make_pep8_name(attribute)
        if pep8_name == 'in':
            pep8_name = '_in'

        assert_dict[pep8_name] = make_caller(dummy, attribute)

    return type('Assert', (object,), assert_dict)


Assert = __make_assert_class()
del __make_assert_class
