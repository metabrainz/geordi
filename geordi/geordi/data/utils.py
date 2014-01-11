from ..db import get_db
import json

def get_item(item_id):
    '''Fetch and return an item's data.'''
    with get_db().cursor() as curs:
        curs.execute('''SELECT '{"blah": "foo", "baz": {"quux": "lol"}}';''')
        data = [json.loads(d[0]) for d in curs.fetchall()]
    return {'id': item_id, 'data': data}

def get_renderable(item_id):
    '''Fetch and return an item's data including a pretty-printed version of the data items.'''
    item = get_item(item_id)
    item['data_formatted'] = [json.dumps(i, indent=4) for i in item.get('data', [])]
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
    if item_id is None:
        item_id = _create_item(data_type)
    _register_data_item(data_id, item_id, data)
    _map_item(item_id)

def match_item(item_id, editor, mbid_type, mbid):
    '''Register a match with an item ID, editor, entity type, and MBID.'''
    pass

def _create_item(data_type):
    with get_db() as conn, conn.cursor() as curs:
        curs.execute('INSERT INTO item (type) VALUES (%s) RETURNING id', (data_type,))
        if curs.rowcount == 1:
            return curs.fetchone()[0]
        else:
            raise Exception('No row created, or more than one.')

def _map_item(item_id):
    # fetch data
    # generate map
    # insert/propagate to relevant databases
    pass

def _register_data_item(item_id, data_id, data):
    with get_db() as conn, conn.cursor() as curs:
        curs.execute('INSERT INTO item_data (id, item, data) VALUES (%s, %s, %s) RETURNING (item, id)', (data_id, item_id, data))
        if curs.rowcount == 1:
            return curs.fetchone()
        else:
            raise Exception('No row created, or more than one created.')
