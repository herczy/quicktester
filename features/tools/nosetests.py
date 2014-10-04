from __future__ import print_function

import sys
import os
import pprint
from pkg_resources import load_entry_point

sys.path.insert(0, '.')

print('----- BEGIN INFO -----', file=sys.stderr)
print('Path:', file=sys.stderr)
pprint.pprint(sys.path, stream=sys.stderr)
print('Env:', file=sys.stderr)
pprint.pprint(dict(os.environ), stream=sys.stderr)
print('Working dir:', os.getcwd(), file=sys.stderr)
print('----- END INFO -----', file=sys.stderr)

sys.exit(load_entry_point('nose', 'console_scripts', 'nosetests')())
