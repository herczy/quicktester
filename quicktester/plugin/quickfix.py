from __future__ import print_function

import nose
import os.path


class QuickFixPlugin(nose.plugins.Plugin):
    '''Store the exceptions in a vim-friendly, quickfix file.'''

    name = 'quickfix'
    enabled = False
    output_filename = None
    exceptions = None
    allow_irrelevant = False
    file_cache = None

    def options(self, parser, env):
        parser.add_option(
            '-Q', '--quickfix', metavar='QUICKFIX-FILE', default=None,
            help='Write exceptions in a vim-friendly way.'
        )
        parser.add_option(
            '--qf-irrelevant', action='store_true',
            help='Store changes to irrelevant files (i.e. not relative to ' +
                 'the current working directory.'
        )

    def configure(self, options, config):
        if options.quickfix is None:
            return

        self.enabled = True
        self.output_filename = options.quickfix
        self.exceptions = []
        self.allow_irrelevant = options.qf_irrelevant
        self.file_cache = {}

    def addError(self, test, err):
        self.exceptions.append((test, err))

    addFailure = addError

    def finalize(self, result):
        with open(self.output_filename, 'w') as f:
            for test, error in self.exceptions:
                self.__print_qf_trace(f, error[-1])

    def __print_qf_trace(self, stream, tb):
        while tb is not None:
            frame = tb.tb_frame
            filename = os.path.relpath(frame.f_code.co_filename, os.getcwd())
            lineno = frame.f_lineno

            tb = tb.tb_next

            if not self.allow_irrelevant and filename.split(os.path.sep, 1)[0] == '..':
                continue

            line = self.__get_file_line(filename, lineno)
            if line is None:
                continue

            print('{}:{}:{}'.format(filename, lineno, line), file=stream)

    def __get_file_line(self, filename, lineno):
        if not os.path.isfile(filename) or not filename.endswith('.py'):
            return None

        if filename not in self.file_cache:
            with open(filename) as f:
                self.file_cache[filename] = {
                    index + 1: line.strip() for index, line in enumerate(f)
                }

        return self.file_cache[filename].get(lineno, None)
