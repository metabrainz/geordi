# ingestr-server
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

from __future__ import division, absolute_import

from ingestr.mappings.util import use_first_text, alternate_text

import re

class wcd():
    def sparse(self, data):
        target = {'release': {}}
        release = target['release']

        try:
            release['title'] = use_first_text(data['meta_xml']['metadata']['album'])
            release['alternate_titles'] = alternate_text(data['meta_xml']['metadata']['album'])
        except KeyError:
            release['title'] = re.split(' / ', data['meta_xml']['metadata']['title']['text'])[0]
            release['alternate_titles'] = []

        try:
            release['date'] = data['meta_xml']['metadata']['year']['text']
        except:
            release['date'] = None

        try:
            release['artist'] = data['meta_xml']['metadata']['artist']['text']
        except KeyError:
            release['artist'] = data['meta_xml']['metadata']['creator']['text']

        return target

    def full(self, data):
        return self.sparse(data['_source'])
