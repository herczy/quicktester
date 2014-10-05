Feature: git-changes plugin

  As a programmer
  In order to quickly check the tests relevant to my modifications
  I want to run the tests based on the git repository

  Background:
    Given an empty package "example"
      And the plugins are installed
      And a new repository is initialized
      And the test file "example/tests/test_example.py" is created:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(0, 1)

              def test_passing(self):
                  self.assertEqual(1, 1)
          """
      And the test file "example/tests/test_example2.py" is created:
          """
          import unittest

          class TestExample2(unittest.TestCase):
              def test_example2(self):
                  self.assertEqual(0, 1)

              def test_passing2(self):
                  self.assertEqual(1, 1)
          """
      And the module file "example/module.py" is created:
          """
          # Some module
          """
      And all changes are committed

  Scenario: no changes are in the repository
     When the command "nosetests -v --git-changes" is executed
     Then no tests are run

  Scenario: changing a test file runs only the test file
     When the test file "example/tests/test_example.py" is changed:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(1, 1)

              def test_passing(self):
                  self.assertEqual(1, 1)
          """
      And the command "nosetests -v --git-changes" is executed
     Then the following tests are run:
          """
          example.tests.test_example.TestExample.test_example
          example.tests.test_example.TestExample.test_passing
          """

  Scenario: changing a module file runs all tests in the package
     When the test file "example/module.py" is changed:
          """
          # Some module
          # Some change
          """
      And the command "nosetests -v --git-changes" is executed
     Then the following tests are run:
          """
          example.tests.test_example.TestExample.test_example
          example.tests.test_example.TestExample.test_passing
          example.tests.test_example2.TestExample2.test_example2
          example.tests.test_example2.TestExample2.test_passing2
          """
