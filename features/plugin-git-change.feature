Feature: git-changes plugin

  As a programmer
  In order to quickly check the tests relevant to my modifications
  I want to run the tests based on the git repository

  Background:
    Given an empty package "example"
      And the plugins are installed
      And a new repository is initialized
      And the test file "example/tests/test_module.py" is created:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_module(self):
                  self.assertEqual(0, 1)

              def test_passing(self):
                  self.assertEqual(1, 1)
          """
      And the test file "example/tests/test_module2.py" is created:
          """
          import unittest

          class TestExample2(unittest.TestCase):
              def test_module2(self):
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

  Scenario: ignoring non-python files
    Given the root file "junk.txt" is created:
          """
          Some irrelevant content
          """
     When the command "nosetests -v --git-changes" is executed
     Then no tests are run

  Scenario: run tests in newly created modules:
    Given an empty package "newpackage"
      And the test file "newpackage/test_module.py" is created:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_mytest(self):
                  assert 0
          """
     When the command "nosetests -v --git-changes" is executed
     Then the following tests are run:
          """
          newpackage.test_module.TestExample.test_mytest
          """

  Scenario: changing a test file runs only the test file
     When the test file "example/tests/test_module.py" is changed:
          """
          import unittest

          class TestExample(unittest.TestCase):
              def test_module(self):
                  self.assertEqual(1, 1)

              def test_passing(self):
                  self.assertEqual(1, 1)
          """
      And the command "nosetests -v --git-changes" is executed
     Then the following tests are run:
          """
          example.tests.test_module.TestExample.test_module
          example.tests.test_module.TestExample.test_passing
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
          example.tests.test_module.TestExample.test_module
          example.tests.test_module.TestExample.test_passing
          example.tests.test_module2.TestExample2.test_module2
          example.tests.test_module2.TestExample2.test_passing2
          """

  Scenario: changing a module file runs all tests in the package with the name matcher
     When the test file "example/module.py" is changed:
          """
          # Some module
          # Some change
          """
      And the command "nosetests -v --git-changes --filename-mapping match" is executed
     Then the following tests are run:
          """
          example.tests.test_module.TestExample.test_module
          example.tests.test_module.TestExample.test_passing
          """
