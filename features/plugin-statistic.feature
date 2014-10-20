Feature: the command-line statistics tool

  As a programmer
  In order to track my previous test failures and their progression
  I want to see what tests failed in the last few runs

  Background:
    Given an empty package "example"

  Scenario: getting the statistics without previous test runs
     When the command "quicktester-statistics" is executed
     Then the last executed command prints the following:
          """
          0 test(s) out of 0 shown
          """
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

          1 test(s) out of 1 shown
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

          3 test(s) out of 3 shown
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

          1 test(s) out of 1 shown
          """
      And the last executed command passes

  Scenario: only statistics relative to the current working directory are shown by default
    Given the plugins are installed
      And an empty package "other"
     When the test file "example/tests/test_example.py" is created:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(0, 1)
          """
      And the test file "other/test_other.py" is created:
          """
          import unittest

          class TestOtherExample(unittest.TestCase):
              def test_zero_equals_one(self):
                  self.assertEqual(0, 1)
          """
      And the command "nosetests" is executed
      And the command "quicktester-statistics --backlog 1" is executed
      And the command "quicktester-statistics --backlog 1" is executed in "other"
     Then the last two executed commands pass
      And the penultimate executed command prints the following:
          """
          [F] example/tests/test_example.py:example.tests.test_example:TestExample.test_example
          [F] other/test_other.py:other.test_other:TestOtherExample.test_zero_equals_one

          2 test(s) out of 2 shown
          """
      And the last executed command prints the following:
          """
          [F] test_other.py:other.test_other:TestOtherExample.test_zero_equals_one

          1 test(s) out of 2 shown
          """

  Scenario: dump statistics for all cases in the statistics file
    Given the plugins are installed
      And an empty package "other"
     When the test file "example/tests/test_example.py" is created:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(0, 1)
          """
      And the test file "other/test_other.py" is created:
          """
          import unittest

          class TestOtherExample(unittest.TestCase):
              def test_zero_equals_one(self):
                  self.assertEqual(0, 1)
          """
      And the command "nosetests" is executed
      And the command "quicktester-statistics --backlog 1 --show-all-tests" is executed in "other"
     Then the last executed command passes
      And the last executed command prints the following:
          """
          [F] ../example/tests/test_example.py:example.tests.test_example:TestExample.test_example
          [F] test_other.py:other.test_other:TestOtherExample.test_zero_equals_one

          2 test(s) out of 2 shown
          """

  Scenario: dump statistics for only the failing cases in the statistics file
    Given the plugins are installed
     When the test file "example/tests/test_example.py" is created:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(0, 1)

              def test_passing(self):
                  self.assertEqual(1, 1)
          """
      And the command "nosetests" is executed
      And the command "quicktester-statistics --backlog 1 --only-failing" is executed
     Then the last executed command passes
      And the last executed command prints the following:
          """
          [F] example/tests/test_example.py:example.tests.test_example:TestExample.test_example

          1 test(s) out of 2 shown
          """
