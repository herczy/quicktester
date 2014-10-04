Feature: the command-line statistics tool

  As a programmer
  In order to quickly check the fixes I wrote for failing tests
  I want to rerun the failing tests only

  Background:
    Given a freshly-cloned git repository with some tests
      And the plugins are accessible

  Scenario: fixing a test and rerunning only the previously failed tests
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
      And nose is run again with the failing tests and passes
     Then only the "quicktester.tests.test_example.TestExample.test_example" tests has beed rerun
