Feature: the command-line statistics tool

  As a programmer
  In order to track my previous test failures and their progression
  I want to see what tests failed in the last few runs

  Background:
    Given a freshly-cloned git repository with some tests

  Scenario: getting the statistics without previous test runs
     When the CLI tool is executed
     Then it does not print anything
