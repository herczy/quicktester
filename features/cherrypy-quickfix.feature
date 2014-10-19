Feature: play nice with cherrpy page tests

  As a CherryPy loving developer
  In order to develop my tests with TDD
  I want to be able to use the quicktester plugins

  @require-package:cherrypy
  Scenario: the complete trace can be shown with an extra option even for cherrypy tests
    Given an empty package "example"
      And the plugins are installed
      And the test file "example/tests/test_example.py" is created:
          """
          import cherrypy
          from cherrypy.test import helper

          class TestCherrypy(helper.CPWebCase):
              @staticmethod
              def setup_server():
                  class Root(object):
                      @cherrypy.expose
                      def index(self):
                          return 'hello, world!'

                  cherrypy.tree.mount(Root())

              def test_example(self):
                  self.getPage('/')

                  self.assertStatus('400 Not found')

              def _handlewebError(self, error):
                  raise self.failureException(error)
          """
     When the command "nosetests -Q $(QUICKFIX)" is executed
     Then the quickfix file has the following content:
          """
          --- AssertionError: Status ('200 OK') != '400 Not found' ---
          example/tests/test_example.py:17:self.assertStatus('400 Not found')
          example/tests/test_example.py:20:raise self.failureException(error)
          """
