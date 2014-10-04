from __future__ import print_function

import json
import sys
import os.path
import pprint
from quicktester.plugin import DEFAULT_STATISTICS_FILE

from pkg_resources import load_entry_point, iter_entry_points, Distribution

print('----- BEGIN INFO -----', file=sys.stderr)

print('Python executable:', sys.executable, file=sys.stderr)

print('Path:', file=sys.stderr)
pprint.pprint(sys.path, stream=sys.stderr)

print('Env:', file=sys.stderr)
pprint.pprint(dict(os.environ), stream=sys.stderr)

print('Working dir:', os.getcwd(), file=sys.stderr)

plugins = pprint.pformat(list(ep.name for ep in iter_entry_points('nose.plugins.0.10')))
print('Installed nose plugins (0.10):', plugins, file=sys.stderr)

if os.path.isfile(DEFAULT_STATISTICS_FILE):
    print('Statistics file:', file=sys.stderr)
    with open(DEFAULT_STATISTICS_FILE) as f:
        pprint.pprint(json.load(f), stream=sys.stderr)

print('----- END INFO -----', file=sys.stderr)

sys.exit(load_entry_point('nose', 'console_scripts', 'nosetests')())
