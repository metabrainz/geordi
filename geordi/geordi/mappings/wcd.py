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
        return {'artist_id': {'name':"artist id", 'key': 'wcd_artist_id'},
                'file': {'name':"file sha1", 'key': 'sha1'},
                'version': 1}

    def code_url(self):
        return "https://github.com/metabrainz/geordi/blob/master/geordi/geordi/mappings/wcd.py"

    def extract_linked(self, data):
        all_artists = []
        files = []
        if 'what_cd_json' in data:
            try:
                main_artists = [self._extract_artist(artist, 'artist') for artist in data['what_cd_json']['response']['group']['musicInfo']['artists']]
                extra_artists = [self._extract_artist(artist, 'with') for artist in data['what_cd_json']['response']['group']['musicInfo']['with']]
                remixers = [self._extract_artist(artist, 'remixer') for artist in data['what_cd_json']['response']['group']['musicInfo']['remixedBy']]
                producers = [self._extract_artist(artist, 'producer') for artist in data['what_cd_json']['response']['group']['musicInfo']['producer']]
                composers = [self._extract_artist(artist, 'composer') for artist in data['what_cd_json']['response']['group']['musicInfo']['composers']]
                conductors = [self._extract_artist(artist, 'conductor') for artist in data['what_cd_json']['response']['group']['musicInfo']['conductor']]
                djs = [self._extract_artist(artist, 'dj') for artist in data['what_cd_json']['response']['group']['musicInfo']['dj']]
                seen = []
                all_artists = [c for c in main_artists if not (c in seen or seen.append(c))]
                all_artists.extend([c for c in extra_artists if not (c in seen or seen.append(c))])
                all_artists.extend([c for c in remixers if not (c in seen or seen.append(c))])
                all_artists.extend([c for c in producers if not (c in seen or seen.append(c))])
                all_artists.extend([c for c in composers if not (c in seen or seen.append(c))])
                all_artists.extend([c for c in conductors if not (c in seen or seen.append(c))])
                all_artists.extend([c for c in djs if not (c in seen or seen.append(c))])
            except: pass
        if 'files_xml' in data:
            try:
                files = [self._extract_file(x) for x in self._linkable_files(data)]
            except: pass
        return {u'artist_id': all_artists, u'file': files, 'version': 2}

    def automatic_item_matches(self, data):
        matches = {}
        try:
            matches['release'] = [re.sub('^urn:mb_release_id:', '', r) for r in collect_text(data['meta_xml']['metadata']['external-identifier'], 'urn:mb_release_id:')]
            matches['release-group'] = [re.sub('^urn:mb_releasegroup_id:', '', r) for r in collect_text(data['meta_xml']['metadata']['external-identifier'], 'urn:mb_releasegroup_id:')]
        except KeyError: pass
        return matches

    def automatic_subitem_matches(self, data):
        matches = {}
        try:
            for f in self._linkable_files(data):
                try:
                    matches['file-{}'.format(f['sha1']['text'])] = {'recording': [re.sub('^urn:mb_recording_id:', '', r) for r in collect_text(f['external-identifier'], 'urn:mb_recording_id:')]}
                except: pass
        except KeyError: pass
        return matches

    def _linkable_files(self, data):
        return [f for f in data['files_xml']['files']['file'] if (f['_source'] == 'original' and 'sha1' in f and f['format']['text'] in self._acceptable_formats())]

    def _acceptable_formats(self):
        return ['Flac', '24bit Flac', 'VBR MP3', 'Ogg Vorbis', 'Apple Lossless Audio']

    def _extract_artist(self, artist, atype):
        return {u'name': unicode(artist['name']), u'wcd_artist_id': int(artist['id']), u'type': atype}

    def _extract_file(self, x):
        f = {
            u'sha1': unicode(x['sha1']['text']),
            u'format': unicode(x['format']['text']),
            u'filename': unicode(x['_name'])
            }
        if 'title' in x and x['title'] and 'text' in x['title']:
            f[u'title'] = unicode(x['title']['text'])
        if 'artist' in x and x['artist'] and 'text' in x['artist']:
            f[u'artist'] = unicode(x['artist']['text'])
        if 'length' in x and x['length'] and 'text' in x['length']:
            f[u'length'] = int(float(x['length']['text']) * 1000)
        if 'track' in x and x['track'] and 'text' in x['track']:
            f[u'number'] = unicode(x['track']['text'])
        if 'external-identifier' in x:
            f[u'acoustid'] = [re.sub('^urn:acoustid:', '', acoustid) for acoustid in collect_text(x['external-identifier'], 'urn:acoustid') if acoustid != 'urn:acoustid:unknown']
        return f

    def _extract_track(self, track, links):
        f = {'title': [], 'artist': [], 'length': [], 'length_formatted': [], 'number': [], 'totaltracks': []}
        f['subitem'] = 'file-{}'.format(track['sha1']['text'])
        try:
            f['title'] = [track['title']['text']]
        except (KeyError, TypeError): pass
        try:
            f['artist'] = [{'name': track['artist']['text']}]
            for artist in links['artist_id']:
                if artist['name'] == f['artist'][0]['name']:
                    f['artist'][0]['subitem'] = 'artist_id-{}'.format(artist['wcd_artist_id'])
        except (KeyError, TypeError): pass
        try:
            f['length'] = [int(float(track['length']['text']) * 1000)]
            f['length_formatted'] = [format_track_length(length) for length in f['length']]
        except (KeyError, TypeError): pass
        if 'track' in track and track['track'] and 'text' in track['track']:
            numbers = [re.split('/', track['track']['text'])[0]]
            for num in numbers:
                try:
                    f['number'].append(str(int(num)))
                except ValueError:
                    f['number'].append(num)

            if re.search('/', track['track']['text']):
                numbers = [re.split('/', track['track']['text'])[1]]
                for num in numbers:
                    try:
                        f['totaltracks'].append(str(int(num)))
                    except ValueError:
                        f['totaltracks'].append(num)


        if re.search('(cd|dis[ck])\s*\d+', track['_name'], re.IGNORECASE):
            f['medium'] = [re.search('(cd|dis[ck])\s*(\d+)', track['_name'], re.IGNORECASE).group(2)]
        else:
            f['medium'] = []

        if 'external-identifier' in track:
            f[u'acoustid'] = [re.sub('^urn:acoustid:', '', acoustid) for acoustid in collect_text(track['external-identifier'], 'urn:acoustid') if acoustid != 'urn:acoustid:unknown']
        else:
            f[u'acoustid'] = []

        return f

    def map(self, data):
        target = base_mapping()
        target['version'] = 5
        release = target['release']

        # Release Title
        try:
            title_candidates = collect_text(data['meta_xml']['metadata']['album'])
        except KeyError:
            title_candidates = []
        try:
            title_list = re.split(' / ', data['meta_xml']['metadata']['title']['text'], maxsplit=2)
            if title_list[0] != 'Various Artists':
                title_candidates.append(title_list[0])
            else:
                title_candidates.append(title_list[1])
        except TypeError: pass
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
            except (KeyError, TypeError): pass
        if 'artist' not in release or len(release['artist']) < 1:
            try:
                release['artist'] = [{'name': name} for name in collect_text(data['meta_xml']['metadata']['artist'])]
            except KeyError:
                release['artist'] = [{'name': name} for name in collect_text(data['meta_xml']['metadata']['creator'])]
        release['combined_artist'] = comma_list([artist['name'] for artist in release['artist']])

        try:
            if data['what_cd_json']['response']['group']['recordLabel']:
                release['label'] = [{'name': data['what_cd_json']['response']['group']['recordLabel']}]
        except: pass

        try:
            if data['what_cd_json']['response']['group']['catalogueNumber']:
                release['catalog_number'] = [data['what_cd_json']['response']['group']['catalogueNumber']]
        except: pass

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
