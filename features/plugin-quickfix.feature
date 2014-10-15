Feature: fail-only plugin

  As a programmer
  In order to be able to quickly navigate the problematic code
  I want to be able to see the exceptions in the quickfix feature

  Background:
    Given an empty package "example"
      And the plugins are installed

  Scenario: requesting a quickfix file will contain the failures in the specified format
    Given the test file "example/tests/test_example.py" is created:
          """
          import unittest
          import os

          class TestFilesystem(unittest.TestCase):
              def test_example(self):
                  os.makedirs('/a/b/c')
          """
     When the command "nosetests -Q $(QUICKFIX) -s" is executed
     Then the quickfix file has the following content:
          """
          --- OSError: [Errno 13] Permission denied: '/a' ---
          example/tests/test_example.py:6:os.makedirs('/a/b/c')
          """

  Scenario: the complete trace can be shown with an extra option
    Given the test file "example/tests/test_example.py" is created:
          """
          import unittest
          import os

          class TestFilesystem(unittest.TestCase):
              def test_example(self):
                  os.makedirs('/a/b/c')
          """
     When the command "nosetests -Q $(QUICKFIX) --qf-irrelevant" is executed
     Then the quickfix file contains the following line:
          """
          example/tests/test_example.py:6:os.makedirs('/a/b/c')
          """
      And there are some other lines too

  @require-python-version:3
  Scenario: in Python 3+, the whole cause chain is displayed
    Given the test file "example/tests/test_example.py" is created:
          """
          import unittest
          import os

          class TestFilesystem(unittest.TestCase):
              def test_example(self):
                  try:
                      os.makedirs('/a/b/c')

                  except Exception as exc:
                      raise RuntimeError('Error') from exc
          """
     When the command "nosetests -Q $(QUICKFIX)" is executed
     Then the quickfix file has the following content:
          """
          --- RuntimeError: Error ---
          example/tests/test_example.py:10:raise RuntimeError('Error') from exc
          --- OSError: [Errno 13] Permission denied: '/a' ---
          example/tests/test_example.py:7:os.makedirs('/a/b/c')
          """

  @require-python-version:3
  Scenario: in Python 3+, the whole context chain is displayed
    Given the test file "example/tests/test_example.py" is created:
          """
          import unittest
          import os

          class TestFilesystem(unittest.TestCase):
              def test_example(self):
                  try:
                      os.makedirs('/a/b/c')

                  except Exception as exc:
                      raise RuntimeError('Error')
          """
     When the command "nosetests -Q $(QUICKFIX)" is executed
     Then the quickfix file has the following content:
          """
          --- RuntimeError: Error ---
          example/tests/test_example.py:10:raise RuntimeError('Error')
          --- OSError: [Errno 13] Permission denied: '/a' ---
          example/tests/test_example.py:7:os.makedirs('/a/b/c')
          """
