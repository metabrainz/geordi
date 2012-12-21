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

from __future__ import division, absolute_import

from geordi import app, es
from geordi.matching import register_match
from geordi.utils import check_data_format
from pyelasticsearch import ElasticHttpNotFoundError

from geordi.mappings.wcd import wcd

class_map = {
    'wcd': wcd()
}

def get_map_by_index(index, data):
    if index in class_map:
        return class_map[index].map(data)

def get_code_url_by_index(index):
    if index in class_map:
        return class_map[index].code_url()

def get_link_types_by_index (index):
    if index in class_map:
        return class_map[index].link_types()

def get_automatic_item_matches_by_index(index, data):
    if index in class_map:
        return class_map[index].automatic_item_matches(data)

def get_automatic_subitem_matches_by_index(index, data):
    if index in class_map:
        return class_map[index].automatic_subitem_matches(data)

def update_map_by_index(index, item, data):
    if index in class_map:
        try:
            document = es.get(index, 'item', item)
        except ElasticHttpNotFoundError:
            return None

        data = document['_source']
        version = document['_version']

        data = check_data_format(data)

        currentmapping = data['_geordi']['mapping']
        mapping = get_map_by_index(index, data)

        if not currentmapping['version'] == mapping['version']:
            data['_geordi']['mapping'] = mapping
            try:
                es.index(index, 'item', data, id=item, es_version=version)
                return True
            except:
                return None
        else:
            return False

def update_linked_by_index(index, item, data):
    if index in class_map:
        try:
            document = es.get(index, 'item', item)
        except ElasticHttpNotFoundError:
            return None

        data = document['_source']
        version = document['_version']

        data = check_data_format(data)

        links = class_map[index].extract_linked(data)
        currentlinks = data['_geordi']['links']['links']
        same = True

        try:
            if (len(links.keys()) != len(currentlinks.keys()) or
                [len(link[1]) for link in links.iteritems() if link[0] != 'version'] != [len(link[1]) for link in currentlinks.iteritems() if link[0] != 'version']):
                same = False
            else:
                for category in class_map[index].link_types().keys():
                    if links[category] != currentlinks[category]:
                        same = False
        except:
            same = False

        if not same:
            data['_geordi']['links']['links'] = links
            try:
                es.index(index, 'item', data, id=item, es_version=version)
                return True
            except:
                return None
        else:
            return False

def update_automatic_item_matches_by_index(index, item, data):
    if index in class_map:
        data = check_data_format(data)
        matches = get_automatic_item_matches_by_index(index, data)
        fakeip = 'internal, matched by index {}'.format(index)
        automatches = data['_geordi']['matchings']['auto_matchings']
        changed = False
        order = ['work', 'recording', 'label', 'artist', 'release', 'release_group']
        # Do matches with more linked items first, then supersede with fewer-ID matches
        for (matchtype, mbids) in sorted(matches.iteritems(), key=lambda x: (len(x[1]), order.index(x[0]) if x[0] in order else 999), reverse=True):
            if (fakeip not in [match.get('ip') for match in automatches] or
                ",".join(sorted(mbids)) not in [",".join(sorted(match.get('mbid', []))) for match in automatches]):
                register_match(index, item, 'item', matchtype, mbids, auto=True, user='matched by index', ip=fakeip)
                changed = True
            else: continue
        return changed

def update_automatic_subitem_matches_by_index(index, item, data):
    if index in class_map:
        data = check_data_format(data)
        matches = get_automatic_subitem_matches_by_index(index, data)
        fakeip = 'internal, matched by index {}'.format(index)
        order = ['work', 'recording', 'label', 'artist', 'release', 'release_group']
        changed = False
        for (subitem_id, subitem_matches) in matches.iteritems():
            try:
                document = es.get(index, 'subitem', subitem_id)
                data = document['_source']
            except ElasticHttpNotFoundError:
                data = {}

            data = check_data_format(data)
            automatches = data['_geordi']['matchings']['auto_matchings']
            # Do matches with more linked items first, then supersede with fewer-ID matches
            for (matchtype, mbids) in sorted(subitem_matches.iteritems(), key=lambda x: (len(x[1]), order.index(x[0]) if x[0] in order else 999), reverse=True):
                if (fakeip not in [match.get('ip') for match in automatches] or
                    ",".join(sorted(mbids)) not in [",".join(sorted(match.get('mbid', []))) for match in automatches]):
                    register_match(index, subitem_id, 'subitem', matchtype, mbids, auto=True, user='matched by index', ip=fakeip)
                    changed = True
                else: continue
        return changed

def map_search_data(data):
    maps = []
    try:
        for result in data['hits']['hits']:
            try:
                maps.append(get_map_by_index(result['_index'], result['_source']))
            except:
                maps.append(None)
        return maps
    except TypeError:
        return None

def get_mapoptions(mapping):
    options = {'mediums': False, 'totaltracks': False, 'acoustid': False}
    for track in mapping['release']['tracks']:
        if len(track['medium']) > 0:
            options['mediums'] = True
        if len(track['totaltracks']) > 0:
            options['totaltracks'] = True
        if len(track['acoustid']) > 0:
            options['acoustid'] = True
        if options['mediums'] and options['totaltracks'] and options['acoustid']:
            break
    return options
