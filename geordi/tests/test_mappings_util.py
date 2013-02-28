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
import geordi.mappings.util

class TestMappingsUtil(unittest.TestCase):

    def test_comma_list(self):
        lst = ["aap", "noot", "mies", "aap", "mies"]
        result = geordi.mappings.util.comma_list(lst)
        expected = "aap, noot, mies, aap and mies"

        self.assertEqual(result, expected)

    def test_comma_only_list(self):
        lst = ["aap", "noot", "mies", "aap", "mies"]
        result = geordi.mappings.util.comma_only_list(lst)
        expected = "aap, noot, mies, aap, mies"

        self.assertEqual(result, expected)

    def test_base_mapping_release(self):
        release_mapping = geordi.mappings.util.base_mapping('release')
        self.assertTrue('version' in release_mapping)
        self.assertTrue('release' in release_mapping)
        props = ['title', 'date', 'artist', 'other_artist', 'label',
                 'catalog_number', 'combined_artist', 'tracks', 'urls']
        for prop in props:
            self.assertTrue(prop in release_mapping['release'])

    def test_base_mapping_track(self):
        track_mapping = geordi.mappings.util.base_mapping('track')
        expected = {'title': [],
                    'artist': [],
                    'length': [],
                    'length_formatted': [],
                    'number': [],
                    'totaltracks': []}
        self.assertEqual(track_mapping, expected)
