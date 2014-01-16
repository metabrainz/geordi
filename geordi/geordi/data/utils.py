from ..db import get_db
import json

def get_item(item_id):
    '''Fetch and return an item's data.'''
    with get_db().cursor() as curs:
        curs.execute('SELECT id, data FROM item_data WHERE item = %s;', (item_id,))
        if curs.rowcount > 0:
            data = dict([(d[0], json.loads(d[1])) for d in curs.fetchall()])
            return {'id': item_id, 'data': data}
        else:
            return None

def get_renderable(item_id):
    '''Fetch and return an item's data including a pretty-printed version of the data items.'''
    item = get_item(item_id)
    if item is not None:
        item['data_formatted'] = dict([(d_id, json.dumps(data, indent=4)) for d_id, data in item.get('data', {}).iteritems()])
    return item

def data_to_item(data_id):
    '''Resolve a data ID to its associated item ID, if it has one (it should!)'''
    item_id = None
    with get_db().cursor() as curs:
        curs.execute('SELECT item FROM item_data WHERE id = %s', (data_id,))
        if curs.rowcount == 1:
            (item_id,) = curs.fetchone()
        elif curs.rowcount > 1:
            raise Exception('More than one item found, that can\'t be right')
    return item_id

def add_data_item(data_id, data_type, data):
    '''Add or update a data item given an ID, type, and data. Create a new item, for additions.'''
    item_id = data_to_item(data_id)
    with get_db() as conn:
        if item_id is None:
            item_id = _create_item(data_type, conn)
        _register_data_item(item_id, data_id, data, conn)
        _map_item(item_id, conn)

def delete_data_item(data_id):
    with get_db() as conn, conn.cursor() as curs:
        curs.execute('DELETE FROM item_data WHERE id = %s RETURNING item', (data_id,))
        item = curs.fetchone()[0]
        curs.execute('DELETE FROM item WHERE id = %s AND NOT EXISTS (SELECT true FROM item_data WHERE item = item.id)', (item,))

def match_item(item_id, editor, mbid_type, mbid):
    '''Register a match with an item ID, editor, entity type, and MBID.'''
    pass

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

def _map_item(item_id, conn):
    # fetch data
    # generate map
    # insert/propagate to relevant databases
    pass

def _register_data_item(item_id, data_id, data, conn):
    with conn.cursor() as curs:
        curs.execute('INSERT INTO item_data (id, item, data) VALUES (%s, %s, %s) RETURNING (item, id)', (data_id, item_id, data))
        if curs.rowcount == 1:
            return curs.fetchone()
        else:
            raise Exception('No row created, or more than one created.')
