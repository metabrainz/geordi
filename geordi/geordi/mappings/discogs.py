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

from geordi.mappings.util import collect_text, collect_obj, base_mapping, MappingBase
from geordi.utils import uniq
import re

class discogs(MappingBase):
    def link_types(self):
        return {
            'artist': {
                'name': "artist id",
                'key': 'artist_id',
                'type': ['artist']
            },
            'label': {
                'name': "label id",
                'key': 'label_id',
                'type': ['label']
            },
            'master': {
                'name': "master id",
                'key': 'master_id',
                'type': ['master']
            },
            'version': 1
        }

    def code_url(self):
        return self.code_url_pattern().format('discogs')

    def extract_linked(self, data):
        artists = labels = masters = []
        try:
            artists = [{'artist_id': artist['id']['text'], 'name': artist['name']['text']} for artist in collect_obj(data['discogs']['artist'])]
        except: pass

        try:
            labels = [{'label_id': label['id']['text'], 'name': label['name']['text']} for label in collect_obj(data['discogs']['label'])]
        except: pass

        try:
            masters = [{'master_id': master['_id'], 'title': master['title']['text']} for master in collect_obj(data['discogs']['master'])]
        except: pass

        return {u'artist': artists, u'label': labels, u'master': masters, 'version': 3}

    def automatic_item_matches(self, data):
        return {}

    def automatic_subitem_matches(self, data):
        return {}

    def map(self, data):
        target = base_mapping('release')
        target['version'] = 6
        release = target['release']

        try:
            release['title'] = collect_text(data['discogs']['release']['title'])
        except: pass

        try:
            release['date'] = collect_text(data['discogs']['release']['released'])
        except: pass

        try:
            release['artist'] = [{'name': artist['name']['text'], 'subitem': 'artist-{0}'.format(int(artist['id']['text']))} for artist in collect_obj(data['discogs']['release']['artists']['artist'])]
            release['combined_artist'] = comma_list([artist['name'] for artist in release['artist']])
        except: pass

        try:
            release['urls'] = [{'url': image['_uri'], 'type': 'cover art'} for image in collect_obj(data['discogs']['release']['images']['image'])]
        except: pass

        return target
