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

from ingestr.mappings.util import use_first_text, alternate_text, concatenate_text, collect_text, comma_list, base_mapping

import re

class wcd():
    def link_types(self):
        return [
                {'name':"wcd artist id", 'key': 'wcd_artist_id'},
                {'name':"wcd file", 'key': 'sha1'}
                ]

    def extract_linked(self, data):
        all_artists = []
        files = []
        if 'what_cd_json' in data:
            main_artists = [{u'name': unicode(artist['name']), u'wcd_artist_id': int(artist['id'])} for artist in data['what_cd_json']['response']['group']['musicInfo']['artists']]
            extra_artists = [{u'name': unicode(artist['name']), u'wcd_artist_id': int(artist['id'])} for artist in data['what_cd_json']['response']['group']['musicInfo']['with']]
            remixers = [{u'name': unicode(artist['name']), u'wcd_artist_id': int(artist['id'])} for artist in data['what_cd_json']['response']['group']['musicInfo']['remixedBy']]
            producers = [{u'name': unicode(artist['name']), u'wcd_artist_id': int(artist['id'])} for artist in data['what_cd_json']['response']['group']['musicInfo']['producer']]
            composers = [{u'name': unicode(artist['name']), u'wcd_artist_id': int(artist['id'])} for artist in data['what_cd_json']['response']['group']['musicInfo']['composers']]
            conductors = [{u'name': unicode(artist['name']), u'wcd_artist_id': int(artist['id'])} for artist in data['what_cd_json']['response']['group']['musicInfo']['conductor']]
            djs = [{u'name': unicode(artist['name']), u'wcd_artist_id': int(artist['id'])} for artist in data['what_cd_json']['response']['group']['musicInfo']['dj']]
            seen = []
            all_artists = [c for c in main_artists if not (c in seen or seen.append(c))]
            all_artists.extend([c for c in extra_artists if not (c in seen or seen.append(c))])
            all_artists.extend([c for c in remixers if not (c in seen or seen.append(c))])
            all_artists.extend([c for c in producers if not (c in seen or seen.append(c))])
            all_artists.extend([c for c in composers if not (c in seen or seen.append(c))])
            all_artists.extend([c for c in conductors if not (c in seen or seen.append(c))])
            all_artists.extend([c for c in djs if not (c in seen or seen.append(c))])
        if 'files_xml' in data:
            files = [{u'sha1': x['sha1']['text']} for x in data['files_xml']['files']['file'] if (x['_source'] == 'original' and 'sha1' in x)]
        return [all_artists, files]

    def sparse(self, data):
        target = base_mapping()
        release = target['release']

        try:
            title_candidates = collect_text(data['meta_xml']['metadata']['album'])
        except KeyError:
            title_candidates = []
        title_candidates.append(re.split(' / ', data['meta_xml']['metadata']['title']['text'], maxsplit=1)[0])
        seen = []
        release['title'] = [c for c in title_candidates if not (c in seen or seen.append(c))]

        try:
            release['date'] = data['meta_xml']['metadata']['year']['text']
        except:
            release['date'] = None

        if 'what_cd_json' in data:
            try:
                release['artist'] = [{'name': artist['name'], 'wcd_artist_id': int(artist['id'])} for artist in data['what_cd_json']['response']['group']['musicInfo']['artists']]
            except KeyError: pass
        if 'artist' not in release or len(release['artist']) < 1:
            try:
                release['artist'] = [{'name': name} for name in collect_text(data['meta_xml']['metadata']['artist'])]
            except KeyError:
                release['artist'] = [{'name': name} for name in collect_text(data['meta_xml']['metadata']['creator'])]

        release['combined_artist'] = comma_list([artist['name'] for artist in release['artist']])

        return target

    def full(self, data):
        return self.sparse(data['_source'])
