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

from ingestr import app
from ingestr.mappings.wcd import wcd
from pyelasticsearch import ElasticSearch, ElasticHttpNotFoundError

es = ElasticSearch(app.config['ELASTICSEARCH_ENDPOINT'])

class_map = {
    'wcd': wcd()
}

def map_search_data(data):
    try:
        return [map_by_index(result['_index'], result['_source']) for result in data['hits']['hits']]
    except TypeError:
        return None

def map_by_index(index, data):
    if index in class_map:
        return class_map[index].map(data)
    else:
        return None

def get_link_types_by_index (index):
    if index in class_map:
        return class_map[index].link_types()

def update_linked_by_index(index, item, data):
    if index in class_map:
        try:
            document = es.get(index, 'item', item)
        except ElasticHttpNotFoundError:
            return None

        data = document['_source']
        version = document['_version']

        if '_ingestr' not in data:
            data['_ingestr'] = {}
        if 'links' not in data['_ingestr']:
            data['_ingestr']['links'] = []

        links = class_map[index].extract_linked(data)
        currentlinks = data['_ingestr']['links']
        same = True

        if (len(links) != len(currentlinks) or
           [len(link) for link in links] != [len(link) for link in currentlinks]):
            same = False
        else:
            for category in range(len(class_map[index].link_types())):
                if links[category] != currentlinks[category]:
                    same = False

        if not same:
            data['_ingestr']['links'] = links
            try:
                es.index(index, 'item', data, id=item, es_version=version)
                return True
            except:
                return None
        else:
            return True

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
