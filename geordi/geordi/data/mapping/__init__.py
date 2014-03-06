from .indexes import index_dict
from .insert import insert_value, InvalidInsertion
import re
import collections
import logging

from os.path import dirname, abspath
from jsonschema import Draft4Validator
import json

logger = logging.getLogger('geordi.data.mapping')

def _flatten(data):
    logger.debug('_flatten %r', data)
    if isinstance(data, collections.Mapping):
        return dict([(k, _flatten(data[k])) for k in data.keys()])
    elif isinstance(data, list):
        if len(data) > 0 and isinstance(data[0], tuple):
            # note that this throws out link info, which should already have been dealt with
            return [_flatten(d[0]) for d in sorted(data,key=lambda x: x[1])]
        else:
            return [_flatten(d) for d in data]
    else:
        return data

def map_item(item):
    '''Map an item, returning the final mapped data, links, blank nodes, etc.'''
    logger.debug('map_item %r', item)
    mapped_data = {}
    links = []
    if len(item['data'].keys()) <= 1:
        for (data_id, data) in item['data'].iteritems():
            (mapped_data, links) = map_data_item(data_id, data)
            mapped_data[None] = mapped_data[data_id]
            del mapped_data[data_id]
    else:
        raise Exception('unimplemented')
    # merge XXX: implement along with merging of items
    return (_flatten(mapped_data), links)

def map_data_item(data_id, data):
    '''Map a data item, returning the appropriate internal representation for merging/flattening'''
    logger.debug('map_data_item %r %r', data_id, data)
    (index, item_type, specific_identifier) = data_id.split('/', 2)
    if re.search(':', specific_identifier):  # blank node
        return ({data_id: data},[]) # XXX: inflate with orderings, when implementing merging (links?)
    else:
        # initial datastructure assumes at least data for this node
        res = {data_id: {}}
        links = []
        # determine index and item type to use
        # get rules to use
        rules = index_dict.get(index, {}).get(item_type, [])
        if len(rules) == 0:
            raise Exception('no rules found to use')
        for rule in rules:
            if rule.test(data):
                values = rule.run(data)
                # these are (node, destination, value, ordering, link) tuples
                for value in values:
                    # put (value, ordering) pair at destination in node
                    node = data_id
                    if value[0] is not None:
                        node = node + ':' + value[0]
                    # insert in a separate dict by node, then at provided path
                    if value[2] is not None:
                        try:
                            res = insert_value(res, [node] + value[1], tuple(value[2:4]))
                        except InvalidInsertion as failure:
                            if value[4] is not None:
                                logger.info('ignoring an insertion failure since links are provided')
                            else:
                                raise failure
                    # add to links
                    if value[4] is not None:
                        # data item ID, node, destination, linked data item
                        links.append((node, value[1], value[4]))
        return (res,links)

def verify_map(data):
    with open(dirname(abspath(__file__)) + '/../../schema/mapping.json') as sch_file:
        schema = json.load(sch_file)
    validator = Draft4Validator(schema)
    return validator.iter_errors(data)
