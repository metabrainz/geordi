from ..db import get_db
from model.item import Item
from model.item_data import ItemData
from .mapping import map_item, verify_map
import json
import re

def get_item(item_id):
    return Item.get_item(item_id)

def get_renderable(item_id):
    '''Fetch and return an item's data including a pretty-printed version of the data items.'''
    item = get_item(item_id)
    if item is not None:
        item['data_formatted'] = dict([(d_id, json.dumps(data, indent=4)) for d_id, data in item.get('data', {}).iteritems()])
        item['map_formatted'] = json.dumps(item['map'], indent=4)
    return item

def get_indexes():
    return ItemData.get_indexes()

def get_item_types_by_index(index):
    return ItemData.get_item_types_by_index(index)

def get_item_ids(index, item_type):
    return ItemData.get_item_ids(index, item_type)

def data_to_item(data_id):
    return ItemData.data_to_item(data_id)

def add_data_item(data_id, data_type, data, conn=None):
    '''Add or update a data item given an ID, type, and data. Create a new item, for additions.'''
    item_id = original_item_id = data_to_item(data_id)
    if conn is None:
        conn = get_db()
    with conn as conn:
        if item_id is None:
            item_id = _create_item(data_type, conn)
        _register_data_item(item_id, data_id, data, conn, update=original_item_id)
        _map_item(item_id)
    return item_id

def delete_data_item(data_id):
    ItemData.delete_data_item(data_id)

def set_sequences():
    '''Set sequence values back to the max actual value in the tables.'''
    with get_db() as conn, conn.cursor() as curs:
        curs.execute("select coalesce(max(id),0) + 1 from item")
        (restart,) = curs.fetchone()
        curs.execute("ALTER SEQUENCE item_id_seq RESTART %s", (restart,))

def _create_item(data_type, conn):
    with conn.cursor() as curs:
        curs.execute('INSERT INTO item (type) VALUES (%s) RETURNING id', (data_type,))
        if curs.rowcount == 1:
            return curs.fetchone()[0]
        else:
            raise Exception('No row created, or more than one.')

link_type_map = {
    'release%artists': 'artist',
    'release%release_group': 'release_group',
    'release%events': 'area',
    'release%labels': 'label',

    'release%mediums%combined%%tracks%%recording': 'recording',
    'release%mediums%combined%%tracks%%artists': 'artist',
    'release%mediums%split%tracks%%recording': 'recording',
    'release%mediums%split%tracks%%artists': 'artist',
}
def _link_type_to_item_type(link_type):
    '''First try the whole path, then take off the last element, etc.,
       until one matches in link_type_map, or return None.'''
    path = re.sub('%[0-9]+(%|$)', '%\\1', link_type).split('%')
    for i in range(len(path),0,-1):
        prospect = link_type_map.get('%'.join(path[:i]))
        if prospect is not None:
            return prospect
    return None

def _map_item(item_id, conn):
    # fetch data
    item = get_item(item_id)
    # generate map
    (mapped, links) = map_item(item)
    this_mapped = mapped[None]
    if list(verify_map(this_mapped)):
        print "Validation errors in mapping item %s: %r, continuing." % (item_id, list(verify_map(this_mapped)))
    # First, update this item's map
    with conn.cursor() as curs:
        curs.execute('UPDATE item SET map = %s WHERE id = %s', (json.dumps(this_mapped,separators=(',', ':')), item_id))
    # Then, go through the links, creating items as needed with the types designated by their mapping paths
    for (node, destination, data_id) in links:
        link_type = '%'.join([str(d) for d in destination])
        if node is None:
            node_item = item_id
        else:
            node_item = data_to_item(node)
        target_item = data_to_item(data_id)
        if target_item is None:
            target_item = _create_item(_link_type_to_item_type(link_type), conn)
            print "%s -> %s" % (data_id, target_item)
            _register_data_item(target_item, data_id, '{}', conn)
        if node_item is None:
            node_item = _create_item('', conn)
            print "%s -> %s" % (node, node_item)
            _register_data_item(node_item, node, '{}', conn)
        with conn.cursor() as curs:
            curs.execute('SELECT TRUE from item_link WHERE item = %s AND linked = %s AND type = %s', (node_item, target_item, link_type))
            if curs.rowcount == 0:
                curs.execute('INSERT INTO item_link (item, linked, type) VALUES (%s, %s, %s)', (node_item, target_item, link_type))
    # Now that we can be assured any types set by links are already set on the items, insert the maps for other mapped nodes
    for data_id in mapped.keys():
        if data_id is not None:
            verify = list(verify_map(mapped[data_id]))
            if verify:
                print "Validation errors in mapping data item %s: %r, continuing" % (data_id, verify)
            add_data_item(data_id, '', json.dumps(mapped[data_id]), conn=conn)

def _register_data_item(item_id, data_id, data, conn, update=False):
    with conn.cursor() as curs:
        if not update:
            query = 'INSERT INTO item_data (item, data, id) VALUES (%s, %s, %s) RETURNING (item, id)'
        else:
            query = 'UPDATE item_data SET item = %s, data = %s WHERE id = %s RETURNING (item, id)'

        curs.execute(query, (item_id, data, data_id))
        if curs.rowcount == 1:
            return curs.fetchone()
        else:
            raise Exception('No row created, or more than one created.')

#def get_entities(mbid_or_mbids, conn=None, cached=True, type_hint=None):
#    entities = []
#    if isinstance(mbid_or_mbids, basestring):
#        mbids = [mbid_or_mbids]
#        one_result = True
#    else:
#        mbids = mbid_or_mbids
#        one_result = False
#    if conn is None:
#        conn = get_db()
#    with conn.cursor() as curs:
#        if cached:
#            curs.execute('SELECT mbid, type, data FROM entity WHERE mbid = any(%s)', (mbids,))
#            if curs.rowcount > 0:
#                for row in curs.fetchall():
#                    (mbid, mbidtype, data) = row
#                    entity = json.loads(data)
#                    entity['mbid'] = mbid
#                    entity['type'] = mbidtype
#                    entities.push(entity)
#        pass
#    if one_result and len(entities) == 1:
#        return entities[0]
#    elif not one_result:
#        return entities
#    elif len(entities) > 1:
#        raise Exception('More than one result fetching entities, when one expected')
