Feature: the command-line statistics tool

  As a programmer
  In order to track my previous test failures and their progression
  I want to see what tests failed in the last few runs

  Background:
    Given an empty package "example"

  Scenario: getting the statistics without previous test runs
     When the command "quicktester-statistics" is executed
     Then the command does not print anything
      And the command passes

  Scenario: fixing a test and seeing the statistics
    Given the plugins are installed
     When the test file "example/tests/test_example.py" is created:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(0, 1)
          """
      And the command "nosetests" is executed
      And the test file "example/tests/test_example.py" is changed:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(1, 1)
          """
      And the command "nosetests" is executed
      And the command "quicktester-statistics --backlog 2" is executed
     Then the last executed command prints the following:
          """
          [F.] example/tests/test_example.py:example.tests.test_example:TestExample.test_example
          """

  Scenario: adding new tests and seeing the statistics
    Given the plugins are installed
     When the test file "example/tests/test_example.py" is created:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(0, 1)
          """
      And the command "nosetests" is executed
      And the test file "example/tests/test_example.py" is changed:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(1, 1)

              def test_failing(self):
                  self.assertEqual(0, 1)

              def test_error(self):
                  raise KeyError('ERROR')
          """
      And the command "nosetests" is executed
      And the command "quicktester-statistics --backlog 2" is executed
     Then the last executed command prints the following:
          """
          [ E] example/tests/test_example.py:example.tests.test_example:TestExample.test_error
          [F.] example/tests/test_example.py:example.tests.test_example:TestExample.test_example
          [ F] example/tests/test_example.py:example.tests.test_example:TestExample.test_failing
          """
      And the last executed command passes

  Scenario: handling the statistics format introduced in 0.1
    Given the statistics file "statistics" is created:
          """
          [[], [["example/tests/test_example.py", "example.tests.test_example", "TestExample.test_example"]], []]
          """
     When the command "quicktester-statistics --backlog 4 --file statistics" is executed
     Then the last executed command prints the following:
          """
          [  F ] example/tests/test_example.py:example.tests.test_example:TestExample.test_example
          """
      And the last executed command passes
