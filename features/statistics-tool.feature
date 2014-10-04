Feature: the command-line statistics tool

  As a programmer
  In order to track my previous test failures and their progression
  I want to see what tests failed in the last few runs

  Background:
    Given a freshly-cloned git repository with some tests

  Scenario: getting the statistics without previous test runs
     When the CLI tool is executed
     Then it does not print anything

  Scenario: fixing a test and seeing the statistics
    Given the plugins are accessible
     When the test file "quicktester/tests/test_example.py" is created:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(0, 1)
          """
      And nose is run and fails
      And the test file "quicktester/tests/test_example.py" is changed:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(1, 1)
          """
      And nose is run again and passes
      And the CLI tool is executed with a backlog of 2
     Then it prints the following:
          """
          [F.] quicktester/tests/test_example.py:quicktester.tests.test_example:TestExample.test_example
          """
