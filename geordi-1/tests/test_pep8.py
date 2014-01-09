#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import unittest

# Shamelessly cribbed from
# https://github.com/Freso/MusicBottle/blob/master/tests.py
# GPLv2
class CodeStyleTestCase(unittest.TestCase):
    """Tests that the code complies to coding style."""
    def setUp(self):
        self.files_to_check = self.find_files()

    def exclude_directory(self, directory):
        """Checks if a given directory should be excluded from the test."""
        # Exclude .hidden directories (e.g., .git, .tx).
        if directory[:1] == '.':
            return True
        if directory == 've':
            return True
        return False

    def include_file(self, filename):
        """Check if a given file should be included in the test."""
        # Only include Python files for now.
        if filename[-3:] == '.py':
            return True
        return False

    def find_files(self):
        import os
        py_files = []
        # Check if we're in the geordi subdir.
        if os.path.isfile('fabfile.py') and os.path.isdir('geordi'):
            for node in os.listdir(os.curdir):
                if os.path.isfile(node) and self.include_file(node):
                    py_files += [os.path.abspath(node)]
                elif os.path.isdir(node) and not self.exclude_directory(node):
                    for dirpath, dirnames, filenames in os.walk(node):
                        # Set dirpath to be absolute, saving the trouble later.
                        dirpath = os.path.abspath(dirpath)
                        for filename in filenames:
                            if self.include_file(filename):
                                py_files += [os.path.join(dirpath, filename)]
        else:
            #@TODO: Actually err out and stop the testcase somehow.
            print("We're not in the root of the project. Aborting this test.")
        return py_files

    def test_pep8_compliance(self):
        """Test that we comply with PEP 8."""
        import pep8
        ignore = ['E302', 'E701', 'E501']
        pep8style = pep8.StyleGuide(ignore=ignore)
        result = pep8style.check_files(self.files_to_check)
        self.assertEqual(result.total_errors, 0,
                         "Found code style errors (and warnings).")
