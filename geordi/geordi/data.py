# geordi
# Copyright (C) 2013 Ian McEwen, MetaBrainz Foundation
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
from flask import request, json
from geordi import es
from geordi.search import do_search, do_search_raw, do_subitem_search, make_filters
from geordi.mappings import map_search_data, update_map_by_index, update_linked_by_index, get_link_types_by_index, update_automatic_item_matches_by_index, update_automatic_subitem_matches_by_index
from geordi.utils import check_data_format

from pyelasticsearch import ElasticHttpNotFoundError

def resolve_data(index, item):
    "Shared data-update functionality"
    data = es.get(index, 'item', item)
    linked_update = update_linked_by_index(index, item, data['_source'])
    map_update = update_map_by_index(index, item, data['_source'])
    match_update = update_automatic_item_matches_by_index(index, item, data['_source'])
    if linked_update or map_update or match_update:
        data = es.get(index, 'item', item)
    update_automatic_subitem_matches_by_index(index, item, data['_source'])
    return data

def get_search_params():
    "Shared search functionality"
    search_type = request.args.get('type', 'query')
    start_from = request.args.get('from', "0")
    query = request.args.get('query')
    indices = request.args.getlist('index')
    itemtypes = request.args.getlist('itemtype')
    size = request.args.get('size', None)
    if size is not None:
        size = int(size)
    if size is not None and size == 10:
        size = None

    if len(itemtypes) == 0:
        itemtypes = ['item']

    filters = make_filters(human=request.args.get('human', False), auto=request.args.get('auto', False), un=request.args.get('un', False))

    if search_type == 'raw':
        json_query = json.loads(query)
        if size is None and 'size' in json_query:
            try:
                size = int(json_query['size'])
            except:
                pass
        try:
            data = do_search_raw(json_query, indices, start_from=request.args.get('from', None), filters=filters, doc_type=itemtypes, size=size)
        except ValueError:
            return {'error': "Malformed or missing JSON."}
    elif search_type == 'query':
        if query:
            data = do_search(query, indices, start_from=request.args.get('from', None), filters=filters, doc_type=itemtypes, size=size)
        else:
            return {'error': 'You must provide a query.'}
    elif search_type == 'sub':
        index = request.args.get('subitem_index')
        subtype = request.args.get('subitem_type')
        if subtype not in get_link_types_by_index(index).keys():
            return {'error': 'Invalid subitem type for index {}'.format(index)}
        data = do_subitem_search(query, index, subtype, start_from=request.args.get('from', None), filters=filters, size=size)
    else:
        return {'error': 'Search type {} unimplemented.'.format(search_type)}

    mapping = map_search_data(data)

    return {"start_from": start_from, "query": query, "mapping": mapping, "data": data, "page_size": size}

def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el

def get_subitem(index, subitem, create=False, seed={}):
    try:
        document = es.get(index, 'subitem', subitem)
        if seed == {}:
            return document
        else:
            data = document['_source']
            data = check_data_format(data)
            changed = False
            for key in seed.keys():
                if key not in data:
                    data[key] = seed[key]
                    changed = True
                elif key in data:
                    changed = True
                    try:
                        if unicode(seed[key]) not in [unicode(i) for i in data[key]]:
                            data[key].append(seed[key])
                        changed = True
                    except (AttributeError, TypeError):
                        data[key] = list(flatten([data[key], seed[key]]))
                        changed = True
                    if isinstance(data[key], collections.Iterable) and not isinstance(data[key], basestring):
                        data[key] = list(set(flatten(data[key])))
            if changed:
                es.index(index, 'subitem', data, id=subitem)
                document = es.get(index, 'subitem', subitem)
            return document
    except ElasticHttpNotFoundError:
        if create:
            data = check_data_format(seed)
            es.index(index, 'subitem', data, id=subitem)
        return None
