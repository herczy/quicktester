Feature: fail-only plugin

  As a programmer
  In order to be able to quickly navigate the problematic code
  I want to be able to see the exceptions in the quickfix feature

  Background:
    Given an empty package "example"
      And the plugins are installed
      And the test file "example/tests/test_example.py" is created:
          """
          import unittest
          import os

          class TestFilesystem(unittest.TestCase):
              def test_example(self):
                  os.makedirs('/a/b/c')
          """

  Scenario: requesting a quickfix file will contain the failures in the specified format
     When the command "nosetests -Q $(QUICKFIX) -s" is executed
     Then the quickfix file has the following content:
          """
          example/tests/test_example.py:6:os.makedirs('/a/b/c')
          """

  Scenario: the complete trace can be shown with an extra option
     When the command "nosetests -Q $(QUICKFIX) --qf-irrelevant" is executed
     Then the quickfix file contains the following line:
          """
          example/tests/test_example.py:6:os.makedirs('/a/b/c')
          """
      And there are some other lines too
