Feature: display statistics even if a full test module fails

  As a programmer
  In order to track my previous test failures and their progression
  I want to see what tests failed in the last few runs even if whole modules failed

  Scenario: fixing an import error and seeing the statistics
    Given an empty package "example"
      And the plugins are installed
     When the test file "example/tests/test_example.py" is created:
          """
          import unittest
          import no_such_module_should_ever_exist

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(1, 1)
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
          [E ] example/tests/test_example.py:example.tests.test_example
          [ .] example/tests/test_example.py:example.tests.test_example:TestExample.test_example

          2 test(s) out of 2 shown
          """
