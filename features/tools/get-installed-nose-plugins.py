from pkg_resources import iter_entry_points


for ep in iter_entry_points('nose.plugins.0.10'):
    print(str(ep))
