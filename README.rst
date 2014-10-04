quickrunner
===========

Nose plugins that will only run "relevant tests"

Installation
------------

To install these plugins, run

::

  $ python setup.py install

Usage
-----

To run only tests relevant to the git changes, use:

::

  $ nosetests --git-changes

To run tests that have failed thrice in the last runs, use:

::

  $ nosetests --run-count 3

Test statistics
---------------

To get the test run statistics, use:

::

  $ quicktester-statistics
