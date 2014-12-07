from .indexes import index_dict
from .insert import InvalidInsertion, PathInserter, fix_path
import re
import collections
import logging

from os.path import dirname, abspath
from jsonschema import Draft4Validator
import json

logger = logging.getLogger('geordi.data.mapping')

def _filter_links(links, path):
    return [link for link in links if (link[0] == path[0] and link[1][:len(path)-1] == path)]

def _replace_ident(link, path, identifier, replace):
    relevant_entry = link[1][len(path)-1]
    if isinstance(relevant_entry, tuple) and relevant_entry[1] == identifier:
        return tuple([link[0], link[1][:len(path)-1] + [replace] + link[1][len(path):]] + list(link[2:]))

def _partition_links(links, path, known_keys):
    logger.debug('_partition_links %r %r %r', links, path, known_keys)
    part = dict([(k, []) for k in known_keys])
    if part.get(None) == []:
        raise Exception('None is among partition keys, abort')
    part[None] = []
    for l in links:
        cmp_path = [l[0]] + l[1]
        logger.debug('path for comparison: %r', cmp_path)
        if len(cmp_path) > len(path) and cmp_path[:len(path)] == path and cmp_path[len(path)] in known_keys:
            part[cmp_path[len(path)]].append(l)
        else:
            part[None].append(l)
    logger.debug('partitioned links: %r', part)
    return part

def _tuple_to_link_tuple(t):
    if len(t) >= 3:
        return tuple(t[1:3])
    else:
        return (t[1], t[1])

def _flatten_with_links(data, links, path=[]):
    logger.debug('_flatten_with_links %r %r %r', data, links, path)
    if isinstance(data, collections.Mapping):
        ret = {}
        ret_links = []
        partitioned_links = _partition_links(links, path, data.keys())
        for k in data.keys():
            new_path = path + [k]
            (flat, l) = _flatten_with_links(data[k], partitioned_links[k], new_path)
            ret[k] = flat
            ret_links.extend(l)
        ret_links.extend(partitioned_links[None])
        return (ret, ret_links)
    elif isinstance(data, list):
        ret = []
        ret_links = []
        if len(data) > 0 and isinstance(data[0], tuple):
            partitioned_links = _partition_links(links, path, [_tuple_to_link_tuple(i) for i in data])
            data_sorted = sorted(data, key=lambda x: x[1])
            for i in range(len(data_sorted)):
                k = _tuple_to_link_tuple(data_sorted[i])
                new_links = [_replace_ident(link, path, k[1], i) for link in partitioned_links[k]]
                new_path = path + [i]
                (flat, l) = _flatten_with_links(data_sorted[i][0], new_links, new_path)
                ret.append(flat)
                ret_links.extend(l)
        else:
            partitioned_links = _partition_links(links, path, list(range(len(data))))
            for k in range(len(data)):
                new_path = path + [k]
                (flat, l) = _flatten_with_links(data[k], partitioned_links[k], new_path)
                ret.append(flat)
                ret_links.extend(l)
        ret_links.extend(partitioned_links[None])
        return (ret, ret_links)
    else:
        return (data, links)

def map_item(item):
    '''Map an item, returning the final mapped data, links, blank nodes, etc.'''
    logger.debug('map_item %r', item)
    mapped_data = {}
    links = []
    d = None
    if len(item['data'].keys()) <= 1:
        for (data_id, data) in item['data'].iteritems():
            (mapped_data, links) = _flatten_with_links(*map_data_item(data_id, data))
            mapped_data[None] = mapped_data[data_id]
            del mapped_data[data_id]
    else:
        raise Exception('unimplemented')
    # merge XXX: implement along with merging of items
    return (mapped_data, links)

def map_data_item(data_id, data):
    '''Map a data item, returning the appropriate internal representation for merging/flattening'''
    logger.debug('map_data_item %r %r', data_id, data)
    (index, item_type, specific_identifier) = data_id.split('/', 2)
    if re.search(':', specific_identifier):  # blank node
        return ({data_id: data},[]) # XXX: inflate with orderings, when implementing merging (links?)
    else:
        # initial datastructure assumes at least data for this node
        inserter = PathInserter({data_id: {}})
        links = []
        # determine index and item type to use
        # get rules to use
        rules = index_dict.get(index, {}).get(item_type, [])
        if len(rules) == 0:
            raise Exception('no rules found to use for '+`index`+':'+`item_type`)
        for rule in rules:
            if rule.test(data):
                values = rule.run(data)
                # these are (node, destination, value, link) tuples
                for value in values:
                    # put value at destination in node
                    node = data_id
                    if value[0] is not None:
                        node = node + ':' + value[0]
                    path = fix_path([node] + value[1])
                    # insert in a separate dict by node, then at provided path
                    if value[2] is not None:
                        try:
                            inserter.insert_data(path, value[2])
                        except InvalidInsertion as failure:
                            if value[3] is not None:
                                logger.info('ignoring an insertion failure since links are provided')
                            else:
                                raise failure
                    # add to links
                    if value[3] is not None:
                        # data item ID, node, destination, linked data item
                        links.append((path[0], path[1:], value[3]))
        return (inserter.get_data(),links)

def verify_map(data):
    with open(dirname(abspath(__file__)) + '/../../schema/mapping.json') as sch_file:
        schema = json.load(sch_file)
    validator = Draft4Validator(schema)
    return validator.iter_errors(data)
