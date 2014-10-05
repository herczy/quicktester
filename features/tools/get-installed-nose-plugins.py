import sys
sys.path.insert(0, '.')

from pkg_resources import iter_entry_points, require
require('quicktester')


for ep in iter_entry_points('nose.plugins.0.10'):
    print(str(ep))
