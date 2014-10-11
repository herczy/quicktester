import io
import sys

from ..statistic import Report, Statistic, DatabaseFactory


if sys.version_info.major >= 3:
    StringIO = io.StringIO

else:
    StringIO = io.BytesIO


class FakeConfig(object):
    def __init__(self, test_names=()):
        self.testNames = list(test_names)
