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

from geordi.mappings.util import concatenate_text, collect_text, comma_list, base_mapping, format_track_length

import re

class wcd():
    def link_types(self):
        return {'artist_id': {'name':"wcd artist id", 'key': 'wcd_artist_id'},
                'file': {'name':"wcd file", 'key': 'sha1'},
                'version': 1}

    def extract_linked(self, data):
        all_artists = []
        files = []
        if 'what_cd_json' in data:
            main_artists = [self._extract_artist(artist) for artist in data['what_cd_json']['response']['group']['musicInfo']['artists']]
            extra_artists = [self._extract_artist(artist) for artist in data['what_cd_json']['response']['group']['musicInfo']['with']]
            remixers = [self._extract_artist(artist) for artist in data['what_cd_json']['response']['group']['musicInfo']['remixedBy']]
            producers = [self._extract_artist(artist) for artist in data['what_cd_json']['response']['group']['musicInfo']['producer']]
            composers = [self._extract_artist(artist) for artist in data['what_cd_json']['response']['group']['musicInfo']['composers']]
            conductors = [self._extract_artist(artist) for artist in data['what_cd_json']['response']['group']['musicInfo']['conductor']]
            djs = [self._extract_artist(artist) for artist in data['what_cd_json']['response']['group']['musicInfo']['dj']]
            seen = []
            all_artists = [c for c in main_artists if not (c in seen or seen.append(c))]
            all_artists.extend([c for c in extra_artists if not (c in seen or seen.append(c))])
            all_artists.extend([c for c in remixers if not (c in seen or seen.append(c))])
            all_artists.extend([c for c in producers if not (c in seen or seen.append(c))])
            all_artists.extend([c for c in composers if not (c in seen or seen.append(c))])
            all_artists.extend([c for c in conductors if not (c in seen or seen.append(c))])
            all_artists.extend([c for c in djs if not (c in seen or seen.append(c))])
        if 'files_xml' in data:
            files = [self._extract_file(x) for x in data['files_xml']['files']['file'] if (x['_source'] == 'original' and 'sha1' in x and x['format']['text'] in self._acceptable_formats())]
        return {u'artist_id': all_artists, u'file': files, 'version': 1}

    def _acceptable_formats(self):
        return ['Flac', 'VBR MP3', 'Ogg Vorbis', 'Apple Lossless Audio']

    def _extract_artist(self, artist):
        return {u'name': unicode(artist['name']), u'wcd_artist_id': int(artist['id'])}

    def _extract_file(self, x):
        f = {
            u'sha1': unicode(x['sha1']['text']),
            u'format': unicode(x['format']['text']),
            u'filename': unicode(x['_name'])
            }
        if 'title' in x and 'text' in x['title']:
            f[u'title'] = unicode(x['title']['text'])
        if 'artist' in x and 'text' in x['artist']:
            f[u'artist'] = unicode(x['artist']['text'])
        if 'length' in x and 'text' in x['length']:
            f[u'length'] = int(float(x['length']['text']) * 1000)
        if 'track' in x and 'text' in x['track']:
            f[u'number'] = unicode(x['track']['text'])
        if 'external-identifier' in x:
            f[u'acoustid'] = [re.sub('^urn:acoustid:', '', acoustid) for acoustid in collect_text(x['external-identifier'], 'urn:acoustid') if acoustid != 'urn:acoustid:unknown']
        return f

    def _extract_track(self, track, links):
        f = {}
        f['subitem'] = 'file-{}'.format(track['sha1']['text'])
        f['title'] = [track['title']['text']]
        f['artist'] = [{'name': track['artist']['text']}]
        for artist in links['artist_id']:
            if artist['name'] == f['artist'][0]['name']:
                f['artist'][0]['subitem'] = 'artist_id-{}'.format(artist['wcd_artist_id'])
        f['length'] = [int(float(track['length']['text']) * 1000)]
        f['length_formatted'] = [format_track_length(length) for length in f['length']]
        f['number'] = f['totaltracks'] = []
        if 'track' in track and 'text' in track['track']:
            numbers = [re.split('/', track['track']['text'])[0]]
            for num in numbers:
                try:
                    f['number'].append(str(int(num)))
                except ValueError:
                    f['number'].append(num)


            if re.search('/', track['track']['text']):
                f['totaltracks'] = [int(re.split('/', track['track']['text'])[1])]
            else:
                f['totaltracks'] = []

        if re.search('cd\s*\d+', track['_name'], re.IGNORECASE):
            f['medium'] = [re.search('cd\s*(\d+)', track['_name'], re.IGNORECASE).group(1)]
        else:
            f['medium'] = []

        if 'external-identifier' in track:
            f[u'acoustid'] = [re.sub('^urn:acoustid:', '', acoustid) for acoustid in collect_text(track['external-identifier'], 'urn:acoustid') if acoustid != 'urn:acoustid:unknown']
        else:
            f[u'acoustid'] = []

        return f

    def map(self, data):
        target = base_mapping()
        target['version'] = 1
        release = target['release']

        # Release Title
        try:
            title_candidates = collect_text(data['meta_xml']['metadata']['album'])
        except KeyError:
            title_candidates = []
        title_candidates.append(re.split(' / ', data['meta_xml']['metadata']['title']['text'], maxsplit=1)[0])
        seen = []
        release['title'] = [c for c in title_candidates if not (c in seen or seen.append(c))]

        # Release Date
        try:
            release['date'] = [data['meta_xml']['metadata']['year']['text']]
        except:
            pass

        # Release Artists
        if 'what_cd_json' in data:
            try:
                release['artist'] = [{'name': artist['name'], 'subitem': "artist_id-{}".format(int(artist['id']))} for artist in data['what_cd_json']['response']['group']['musicInfo']['artists']]
            except KeyError: pass
        if 'artist' not in release or len(release['artist']) < 1:
            try:
                release['artist'] = [{'name': name} for name in collect_text(data['meta_xml']['metadata']['artist'])]
            except KeyError:
                release['artist'] = [{'name': name} for name in collect_text(data['meta_xml']['metadata']['creator'])]
        release['combined_artist'] = comma_list([artist['name'] for artist in release['artist']])

        # Tracks
        links = self.extract_linked(data)
        release['tracks'] = sorted([self._extract_track(x, links)
                      for x
                      in data['files_xml']['files']['file']
                      if (x['_source'] == 'original' and x['format']['text'] in self._acceptable_formats())],
                  key=self._track_sorter)

        return target

    def _track_sorter(self, track):
        try:
            tnum = int(track['number'][0])
        except IndexError:
            tnum = 0
        except ValueError:
            tnum = track['number'][0]

        try:
            mnum = int(track['medium'][0])
        except IndexError:
            mnum = 0
        except ValueError:
            mnum = track['medium'][0]

        return (mnum, tnum)
