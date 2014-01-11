from ..db import get_db
import json

def get_item(item_id):
    with get_db().cursor() as curs:
        curs.execute('''SELECT '{"blah": "foo", "baz": {"quux": "lol"}}';''')
        data = [json.loads(d[0]) for d in curs.fetchall()]
    return {'id': item_id, 'data': data}

def get_renderable(item_id):
    item = get_item(item_id)
    item['data_formatted'] = [json.dumps(i, indent=4) for i in item.get('data', [])]
    return item

def data_to_item(data_id):
    item_id = None
    with get_db().cursor() as curs:
        curs.execute('SELECT item FROM item_data WHERE data_id = %s', (data_id,))
        if curs.rowcount == 1:
            (item_id,) = curs.fetchone()
        elif curs.rowcount > 1:
            raise Exception('More than one item found, that can\'t be right')
    return item_id

def add_data_item(data_id, data_type, data):
    item_id = data_to_item(data_id)
    if item_id is None:
        item_id = _create_item(data_type)
        _register_data_item(data_id, item_id)
    # insert actual data as appropriate
    _map_item(item_id)

def match_item(item_id, editor, mbid_type, mbid):
    pass

def _create_item(data_type):
    with get_db() as conn, conn.cursor() as curs:
        curs.execute('INSERT INTO item (type) VALUES (%s) RETURNING id', (data_type,))
        if curs.rowcount == 1:
            return curs.fetchone()[0]
        else:
            raise Exception('No row created, or more than one.')

def _map_item(item_id):
    pass

def _register_data_item(item_id, data_id):
    with get_db() as conn, conn.cursor() as curs:
        curs.execute('INSERT INTO item_data (item, data_id) VALUES (%s, %s) RETURNING (item, data_id)', (item_id, data_id))
        if curs.rowcount == 1:
            return curs.fetchone()
        else:
            raise Exception('No row created, or more than one created.')
