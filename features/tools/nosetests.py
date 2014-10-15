from __future__ import print_function

import sys
sys.path.insert(0, '.')

import os.path
import pprint

from pkg_resources import load_entry_point, iter_entry_points, require
require('quicktester')

if os.getenv('QUICKTESTER_NOSE_PRINT_INFO', 'no') == 'yes':
    print('----- BEGIN INFO -----', file=sys.stderr)

    print('Python executable:', sys.executable, file=sys.stderr)

    print('Path:', file=sys.stderr)
    pprint.pprint(sys.path, stream=sys.stderr)

    print('Env:', file=sys.stderr)
    pprint.pprint(dict(os.environ), stream=sys.stderr)

    print('Working dir:', os.getcwd(), file=sys.stderr)

    plugins = pprint.pformat(list(ep.name for ep in iter_entry_points('nose.plugins.0.10')))
    print('Installed nose plugins (0.10):', plugins, file=sys.stderr)

    print('----- END INFO -----', file=sys.stderr)

sys.exit(load_entry_point('nose', 'console_scripts', 'nosetests')())
