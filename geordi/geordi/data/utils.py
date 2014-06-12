from ..db import get_db
from .mapping import map_item, verify_map
import json
import re

def get_item(item_id, conn=None):
    '''Fetch and return an item's data.'''
    ret = {'id': item_id, 'data': [], 'map': {}, 'type': ''}
    if conn is None:
        conn = get_db()
    with conn.cursor() as curs:
        curs.execute('SELECT id, data FROM item_data WHERE item = %s;', (item_id,))
        if curs.rowcount > 0:
            data = dict([(d[0], json.loads(d[1])) for d in curs.fetchall()])
            ret['data'] = data
        else:
            return None
        curs.execute('SELECT map, type FROM item WHERE id = %s', (item_id,))
        if curs.rowcount > 0:
            row = curs.fetchone()
            if row[0] is not None:
                ret['map'] = json.loads(row[0])
            if row[1] is not None:
                ret['type'] = row[1]
        # XXX: backwards links
        curs.execute('SELECT type, linked FROM item_link WHERE item = %s', (item_id,))
        if curs.rowcount > 0:
            links = dict([(d[0], d[1]) for d in curs.fetchall()])
            ret['links'] = links
        return ret

def get_renderable(item_id):
    '''Fetch and return an item's data including a pretty-printed version of the data items.'''
    item = get_item(item_id)
    if item is not None:
        item['data_formatted'] = dict([(d_id, json.dumps(data, indent=4)) for d_id, data in item.get('data', {}).iteritems()])
        item['map_formatted'] = json.dumps(item['map'], indent=4)
    return item

def get_indexes(conn=None):
    if conn is None:
        conn = get_db()
    with conn.cursor() as curs:
        curs.execute("SELECT DISTINCT regexp_replace(id, '/.*$', '') FROM item_data")
        return [i[0] for i in curs.fetchall()]

def get_item_types_by_index(index, conn=None):
    if conn is None:
        conn = get_db()
    with conn.cursor() as curs:
        curs.execute("SELECT DISTINCT regexp_replace(id, '^[^/]*/([^/]*)/.*$', '\\1') FROM item_data WHERE id ~ ('^' || %s || '/')", (index,))
        return [i[0] for i in curs.fetchall()]

def get_item_ids(index, item_type, conn=None):
    if conn is None:
        conn = get_db()
    with conn.cursor() as curs:
        curs.execute("SELECT DISTINCT regexp_replace(id, '^[^/]*/[^/]*/(.*)$', '\\1') FROM item_data WHERE id ~ ('^' || %s || '/' || %s || '/')", (index, item_type))
        return [i[0] for i in curs.fetchall()]

def data_to_item(data_id, conn=None):
    '''Resolve a data ID to its associated item ID, if it has one (it should!)'''
    item_id = None
    if conn is None:
        conn = get_db()
    with conn.cursor() as curs:
        curs.execute('SELECT item FROM item_data WHERE id = %s', (data_id,))
        if curs.rowcount == 1:
            (item_id,) = curs.fetchone()
        elif curs.rowcount > 1:
            raise Exception('More than one item found, that can\'t be right')
    return item_id

def add_data_item(data_id, data_type, data, conn=None):
    '''Add or update a data item given an ID, type, and data. Create a new item, for additions.'''
    item_id = original_item_id = data_to_item(data_id)
    if conn is None:
        conn = get_db()
    with conn as conn:
        if item_id is None:
            item_id = _create_item(data_type, conn)
        _register_data_item(item_id, data_id, data, conn, update=original_item_id)
        _map_item(item_id, conn)
    return item_id

def delete_data_item(data_id):
    with get_db() as conn, conn.cursor() as curs:
        curs.execute('DELETE FROM item_data WHERE id = %s RETURNING item', (data_id,))
        item = curs.fetchone()[0]
        curs.execute('''DELETE FROM item_link WHERE (item = %s OR linked = %s) AND (
                            NOT EXISTS (SELECT true FROM item_data WHERE item = item_link.item)
                            OR NOT EXISTS (SELECT true FROM item_data WHERE item = item_link.linked)
                        )''', (item,item))
        curs.execute('DELETE FROM item WHERE id = %s AND NOT EXISTS (SELECT true FROM item_data WHERE item = item.id)', (item,))

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
    item = get_item(item_id, conn)
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
            node_item = data_to_item(node, conn=conn)
        target_item = data_to_item(data_id, conn=conn)
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

def get_entities(mbid_or_mbids, conn=None, cached=True, type_hint=None):
    if isinstance(mbid_or_mbids, basestring):
        mbids = [mbid_or_mbids]
        one_result = True
    else:
        mbids = mbid_or_mbids
        one_result = False
    if conn is None:
        conn = get_db()
    with conn.cursor() as curs:
        if cached:
            curs.execute('SELECT mbid, type, data FROM entity WHERE mbid = any(%s)', (mbids,))
