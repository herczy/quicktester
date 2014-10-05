from __future__ import print_function

import re
import sys

from .assertfunc import Assert
from .verify import *
from .path import *
from . import runner


def process_nose_output(output):
    tests = {}
    for line in output.split('\n'):
        m = re.match(r'([a-zA-Z0-9_]+) \(([a-zA-Z0-9_\.]*)\) ... ([^\s]*)', line)
        if m is None:
            continue

        tests[m.group(2) + '.' + m.group(1)] = m.group(3)

    return tests
