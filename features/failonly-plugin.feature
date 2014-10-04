Feature: the command-line statistics tool

  As a programmer
  In order to quickly check the fixes I wrote for failing tests
  I want to rerun the failing tests only

  Background:
    Given an empty package "example"
      And the plugins are installed

  Scenario: fixing a test and rerunning only the previously failed tests
     When the test file "example/tests/test_example.py" is created:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(0, 1)

              def test_passing(self):
                  self.assertEqual(1, 1)
          """
      And nose is run and fails
      And the test file "example/tests/test_example.py" is changed:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(1, 1)

              def test_passing(self):
                  self.assertEqual(1, 1)
          """
      And nose is run again with the failing tests and passes
     Then only the "example.tests.test_example.TestExample.test_example" tests has beed rerun

  Scenario: if the test failed on the first run of four and we only the last three runs, we dont re-run the test
     When the test file "example/tests/test_example.py" is created:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(0, 1)
          """
      And nose is run and fails
      And the test file "example/tests/test_example.py" is changed:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(1, 1)
          """
      And nose is run again 2 times and passes each time
      And nose is run again with the failing tests in the last 4 runs and passes
     Then only the "example.tests.test_example.TestExample.test_example" tests has beed rerun

  Scenario: if the test failed on the first run of three and we check the last three runs, we re-run the test
     When the test file "example/tests/test_example.py" is created:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(0, 1)
          """
      And nose is run and fails
      And the test file "example/tests/test_example.py" is changed:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(1, 1)
          """
      And nose is run again 2 times and passes each time
      And nose is run again with the failing tests in the last 3 runs and passes
     Then only the "example.tests.test_example.TestExample.test_example" tests has beed rerun
