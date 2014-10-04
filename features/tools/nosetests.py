from __future__ import print_function

import sys
import os
import pprint
from pkg_resources import load_entry_point, iter_entry_points

sys.path.insert(0, '.')

print('----- BEGIN INFO -----', file=sys.stderr)
print('Path:', file=sys.stderr)
pprint.pprint(sys.path, stream=sys.stderr)
print('Env:', file=sys.stderr)
pprint.pprint(dict(os.environ), stream=sys.stderr)
print('Working dir:', os.getcwd(), file=sys.stderr)
print('Installed nose plugins (0.10):', file=sys.stderr)
pprint.pprint(list(ep.name for ep in iter_entry_points('nose.plugins.0.10')), stream=sys.stderr)
print('----- END INFO -----', file=sys.stderr)

sys.exit(load_entry_point('nose', 'console_scripts', 'nosetests')())
