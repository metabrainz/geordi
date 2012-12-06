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
    return [map_by_index(result['_index'], result['_source'], sparse=True) for result in data['hits']['hits']]

def map_by_index(index, data, sparse=False):
    if index in class_map:
        if sparse:
            return class_map[index].sparse(data)
        else:
            return class_map[index].full(data)
    else:
        return None

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
           [len(item) for item in links] != [len(item) for item in currentlinks]):
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
