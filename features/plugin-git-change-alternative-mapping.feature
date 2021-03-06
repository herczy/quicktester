Feature: git-changes plugin

  As a programmer
  In order to quickly check the tests relevant to my modifications
  I want to run the tests based on the git repository with my tests in a separate module

  Background:
    Given an empty package "example"
      And an empty package "tests"
      And the plugins are installed
      And the test file "tests/test_module.py" is created:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(0, 1)

              def test_passing(self):
                  self.assertEqual(1, 1)
          """
      And the test file "tests/test_module2.py" is created:
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
      And the module file "example/module2.py" is created:
          """
          # Some other module
          """
      And a new repository is initialized with the new files

  Scenario: ignoring non-python files
    Given the root file "junk.txt" is created:
          """
          Some irrelevant content
          """
     When the command "nosetests -v --git-changes --separate-tests tests" is executed
     Then no tests are run

  Scenario: changing a test file runs only the test file
     When the test file "tests/test_module.py" is changed:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_example(self):
                  self.assertEqual(1, 1)

              def test_passing(self):
                  self.assertEqual(1, 1)
          """
      And the command "nosetests -v --git-changes  --separate-tests tests" is executed
     Then the following tests are run:
          """
          tests.test_module.TestExample.test_example
          tests.test_module.TestExample.test_passing
          """

  Scenario: changing a module file runs all tests in the package
     When the test file "example/module.py" is changed:
          """
          # Some module
          # Some change
          """
      And the command "nosetests -v --git-changes  --separate-tests tests" is executed
     Then the following tests are run:
          """
          tests.test_module.TestExample.test_example
          tests.test_module.TestExample.test_passing
          """
