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
from geordi.mappings import get_link_types_by_index

from pyelasticsearch import ElasticHttpNotFoundError

def do_search(query_string, indices, start_from=None, filters=None, doc_type=['item'], size=None):
    query = {'query':
             {"query_string": {"query": query_string}}}
    return do_search_raw(query, indices, start_from, filters, doc_type, size=size)

def do_subitem_search(query_string, index, subtype,
                      start_from=None, filters=None, size=None):
    link_types = get_link_types_by_index(index)
    key = link_types[subtype]['key']
    query_field = '_geordi.links.links.{subtype}.{key}'.format(subtype=subtype,
                                                               key=key)
    query = {'query':
             {'match': {query_field: query_string}}}
    return do_search_raw(query, [index], start_from, filters, 'item', size=size)

def do_search_raw(query, indices, start_from=None, filters=None, doc_type=['item'], size=None):
    if indices in [[], ['']]:
        indices = app.config['AVAILABLE_INDICES']
    if start_from:
        query['from'] = start_from
    if int(query.get('size', 10)) > 10000:
        query['size'] = 10000
    if filters:
        query['filter'] = filters
    if size:
        query['size'] = size
    return es.search(query, index=indices, doc_type=doc_type)

def make_filters(human=False, auto=False, un=False):
    if human and auto and un:
        return None

    if len([True for ftype in [human, auto, un] if ftype]) > 1:
        filters = {'or': []}
    else:
        filters = {}

    if human:
        thisf = {'query': {'match': {'_geordi.matchings.current_matching.auto': False}}}
        if 'or' in filters:
            filters['or'].append(thisf)
        else:
            filters = thisf
    if auto:
        thisf = {'query': {'match': {'_geordi.matchings.current_matching.auto': True}}}
        if 'or' in filters:
            filters['or'].append(thisf)
        else:
            filters = thisf
    if un:
        thisf = {'missing': {'field': '_geordi.matchings.current_matching.user'}}
        if 'or' in filters:
            filters['or'].append(thisf)
        else:
            filters = thisf
    return filters
