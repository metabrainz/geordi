#!/usr/bin/env python2
# -*- coding: utf-8 -*-

# Copyright 2013 MetaBrainz Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import unittest
import geordi.utils

class TestUtils(unittest.TestCase):

    def test_uniq(self):
        result = geordi.utils.uniq(["aap", "noot", "mies", "aap", "mies"])
        expected = ["aap", "noot", "mies"]

        self.assertEqual(result, expected)

    def test_htmlunescape(self):
        kodakumi = '&#20502;&#30000;&#20358;&#26410;'
        expected = '倖田來未'

        self.assertEqual(geordi.utils.htmlunescape(kodakumi), expected)

    def test_check_data_format(self):
        # Test empty dict ends up correct
        self.assertEqual(geordi.utils.check_data_format({}),
                         {'_geordi':
                             {'mapping': {'version': 0},
                              'links': {'links': [], 'version': 1},
                              'matchings': {'matchings': [],
                                            'auto_matchings': [],
                                            'current_matching': {},
                                            'version': 3}}})

        # Test dict with _geordi key but nothing else works fine
        self.assertEqual(geordi.utils.check_data_format({'_geordi': {}}),
                         {'_geordi':
                             {'mapping': {'version': 0},
                              'links': {'links': [], 'version': 1},
                              'matchings': {'matchings': [],
                                            'auto_matchings': [],
                                            'current_matching': {},
                                            'version': 3}}})
