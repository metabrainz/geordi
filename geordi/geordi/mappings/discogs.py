# geordi
# Copyright (C) 2012 Ian McEwen, MetaBrainz Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division, absolute_import, unicode_literals

from geordi.mappings.util import collect_text, base_mapping, MappingBase
from geordi.utils import uniq
import re

class discogs(MappingBase):
    def link_types(self):
        return {
            'version': 0
        }

    def code_url(self):
        return self.code_url_pattern().format('discogs')

    def extract_linked(self, data):
        return {'version': 0}

    def automatic_item_matches(self, data):
        return {}

    def automatic_subitem_matches(self, data):
        return {}

    def map(self, data):
        target = base_mapping('release')
        target['version'] = 2
        release = target['release']

        try:
            release['title'] = collect_text(data['discogs']['release']['title'])
        except: pass

        try:
            release['date'] = collect_text(data['discogs']['release']['released'])
        except: pass

        return target
