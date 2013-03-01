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
from geordi.mappings.wcd import wcd

class TestMappingsWcd(unittest.TestCase):

    def test_link_types(self):
        linktypes = wcd().link_types()
        self.assertTrue('artist_id' in linktypes)
        self.assertTrue('file' in linktypes)
