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
from geordi.utils import uniq, htmlunescape

import re

class wcd():
    def link_types(self):
        return {'artist_id': {'name':"artist id", 'key': 'wcd_artist_id'},
                'file': {'name':"file sha1", 'key': 'sha1'},
                'version': 1}

    def code_url(self):
        return "https://github.com/metabrainz/geordi/blob/master/geordi/geordi/mappings/wcd.py"

    def extract_linked(self, data):
        all_artists = files = []
        try:
            main_artists = [self._extract_artist(artist, 'artist') for artist in data['what_cd_json']['response']['group']['musicInfo']['artists']]
            extra_artists = [self._extract_artist(artist, 'with') for artist in data['what_cd_json']['response']['group']['musicInfo']['with']]
            remixers = [self._extract_artist(artist, 'remixer') for artist in data['what_cd_json']['response']['group']['musicInfo']['remixedBy']]
            producers = [self._extract_artist(artist, 'producer') for artist in data['what_cd_json']['response']['group']['musicInfo']['producer']]
            composers = [self._extract_artist(artist, 'composer') for artist in data['what_cd_json']['response']['group']['musicInfo']['composers']]
            conductors = [self._extract_artist(artist, 'conductor') for artist in data['what_cd_json']['response']['group']['musicInfo']['conductor']]
            djs = [self._extract_artist(artist, 'dj') for artist in data['what_cd_json']['response']['group']['musicInfo']['dj']]
            all_artists = uniq(main_artists + extra_artists + remixers + producers + composers + conductors + djs)
        except: pass
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
        try:
            f[u'title'] = unicode(x['title']['text'])
        except: pass
        try:
            f[u'artist'] = unicode(x['artist']['text'])
        except: pass
        try:
            f[u'length'] = int(float(x['length']['text']) * 1000)
        except: pass
        try:
            f[u'number'] = unicode(x['track']['text'])
        except: pass
        try:
            f[u'acoustid'] = [re.sub('^urn:acoustid:', '', acoustid) for acoustid in collect_text(x['external-identifier'], 'urn:acoustid(?!:unknown)')]
        except: pass
        return f

    def _extract_track(self, track, links):
        f = base_mapping('track')
        f['subitem'] = 'file-{}'.format(track['sha1']['text'])
        try:
            f['title'] = [track['title']['text']]
        except: pass
        try:
            f['artist'] = [{'name': track['artist']['text']}]
            for artist in links['artist_id']:
                if artist['name'] == f['artist'][0]['name']:
                    f['artist'][0]['subitem'] = 'artist_id-{}'.format(artist['wcd_artist_id'])
        except: pass
        try:
            f['length'] = [int(float(track['length']['text']) * 1000)]
            f['length_formatted'] = [format_track_length(length) for length in f['length']]
        except: pass
        try:
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
        except: pass


        disk_re = re.compile('(cd|dis[ck])\s*(\d+)', re.IGNORECASE)
        if disk_re.search(track['_name']):
            f['medium'] = [disk_re.search(track['_name']).group(2)]
        else:
            f['medium'] = []

        if 'external-identifier' in track:
            f[u'acoustid'] = [re.sub('^urn:acoustid:', '', acoustid) for acoustid in collect_text(track['external-identifier'], 'urn:acoustid(?!:unknown)')]
        else:
            f[u'acoustid'] = []

        return f

    def map(self, data):
        target = base_mapping('release')
        target['version'] = 9
        release = target['release']

        # Release Title
        try:
            title_candidates = [htmlunescape(data['what_cd_json']['response']['group']['name'])]
        except:
            title_candidates = []
        try:
            title_candidates.extend(collect_text(data['meta_xml']['metadata']['album']))
        except: pass
        try:
            title_list = re.split(' / ', data['meta_xml']['metadata']['title']['text'], maxsplit=2)
            if title_list[0] != 'Various Artists':
                title_candidates.append(title_list[0])
            else:
                title_candidates.append(title_list[1])
        except: pass
        release['title'] = uniq(title_candidates)

        # Release Date
        try:
            release['date'] = collect_text(data['meta_xml']['metadata']['year'])
        except: pass

        # Release Artists
        if 'what_cd_json' in data:
            try:
                release['artist'] = [{'name': artist['name'], 'subitem': "artist_id-{}".format(int(artist['id']))} for artist in data['what_cd_json']['response']['group']['musicInfo']['artists']]
            except (KeyError, TypeError): pass
        if 'artist' not in release or len(release['artist']) < 1:
            try:
                release['artist'] = [{'name': name} for name in collect_text(data['meta_xml']['metadata']['artist'])]
            except KeyError:
                try:
                    release['artist'] = [{'name': name} for name in collect_text(data['meta_xml']['metadata']['creator'])]
                except: release['artist'] = []
        release['combined_artist'] = comma_list([artist['name'] for artist in release['artist']])

        # Release Label
        label_candidates = []
        catno_candidates = []
        try:
            if data['what_cd_json']['response']['group']['recordLabel']:
                label_candidates.append(data['what_cd_json']['response']['group']['recordLabel'])
        except: pass
        try:
            tor_id = re.split('_', data['meta_xml']['metadata']['identifier']['text'])[-1]
            for torrent in data['what_cd_json']['response']['torrents']:
                if int(torrent['id']) == int(tor_id):
                    try:
                        if torrent['remasterRecordLabel']:
                            label_candidates.append(torrent['remasterRecordLabel'])
                    except KeyError: pass
                    try:
                        if torrent['remasterCatalogueNumber']:
                            catno_candidates.append(torrent['remasterCatalogueNumber'])
                    except KeyError: pass
                    break
        except KeyError: pass
        try:
            label_candidates.extend(collect_text(data['meta_xml']['metadata']['publisher']))
        except KeyError: pass

        release['label'] = [{'name': name} for name in uniq(label_candidates)]

        # Release Catalog Number
        try:
            if data['what_cd_json']['response']['group']['catalogueNumber']:
                catno_candidates.append(data['what_cd_json']['response']['group']['catalogueNumber'])
        except: pass
        release['catalog_number'] = uniq(catno_candidates)

        # Tracks
        links = self.extract_linked(data)
        try:
            release['tracks'] = sorted([self._extract_track(x, links)
                      for x
                      in data['files_xml']['files']['file']
                      if (x['_source'] == 'original' and x['format']['text'] in self._acceptable_formats())],
                  key=self._track_sorter)
        except: pass

        # URLs
        try:
            release['urls'].append(
                {"url": data['what_cd_json']['response']['group']['wikiImage'],
                 "type": "cover art"}
            )
        except: pass

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
