import os.path
import re
import sys
try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup


sys.path.insert(0, '.')
try:
    import quicktester

finally:
    del sys.path[0]


setup(
    name='quicktester',
    description='quicktester nose plugin set',
    long_description=\
    '''quicktester is a set of plugins that can be used to quickly run
    relevant tests cases.

    The git-changes plugin will only run tests that are relevant to the
    modified files, according to git. The fail-only plugin will only run
    tests that have failed in the last few runs. The statistics plugin
    collects statistics for the fail-only plugin. The quickfix plugin
    helps vim users to have error traces in a quickfix format.
    ''',
    license='BSD',
    version=quicktester.__version__,
    author='Viktor Hercinger',
    author_email='hercinger.viktor@gmail.com',
    maintainer='Viktor Hercinger',
    maintainer_email='hercinger.viktor@gmail.com',
    keywords='test unittest tdd vim quickfix relevant',
    url='http://github.com/herczy/quicktester',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development :: Testing'
    ],
    zip_safe=True,
    use_2to3=False,
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
    requires=['nose'],
    data_files=[
        ('share/quicktester', ['contrib/quicktester.vim']),
    ]
)
