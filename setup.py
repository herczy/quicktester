import os
import re
try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup


with open('requirements.txt') as f:
    requires = [re.sub(r'^([^<>=]*)[<>=]=.*$', r'\1', line.strip()) for line in f if line]


setup(
    name="quicktester",
    description="For running tests quicker",
    license="BSD",
    version="0.1",
    author="Viktor Hercinger",
    author_email="hercinger.viktor@gmail.com",
    maintainer="Viktor Hercinger",
    maintainer_email="hercinger.viktor@gmail.com",
    packages=['quicktester', 'quicktester.plugin'],
    entry_points={
        'console_scripts': [
            'quicktester-statistics = quicktester.plugin.statistic:quicktester_statistics'
        ],
        'nose.plugins.0.10': [
            'statistic = quicktester.plugin.statistic:StatisticsPlugin',
            'fail-only = quicktester.plugin.failonly:FailOnlyPlugin',
            'git-change = quicktester.plugin.git:GitChangesPlugin',
            'quickfix = quicktester.plugin.quickfix:QuickFixPlugin',
        ],
    },
    requires=requires
)
