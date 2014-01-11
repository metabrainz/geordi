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

def add_data(data_id, data_type, data):
    item_id = data_to_item(data_id)
    if item_id is None:
        item_id = create_item(data_type)
        register_data(data_id, item_id)
    # insert actual data to elasticsearch
    map_item(item_id)

def data_to_item(data_id):
    item_id = None
    with get_db().cursor() as curs:
        curs.execute('SELECT item_id FROM item_data WHERE data_id = %s', (data_id,))
        if curs.rowcount == 1:
            (item_id,) = curs.fetchone()
        elif curs.rowcount > 1:
            raise Exception('More than one item found, that can\'t be right')
    return item_id

def map_item(item_id):
    pass

def create_item(data_type):
    with get_db() as conn, conn.cursor() as curs:
        curs.execute('INSERT INTO item (type) VALUES (%s) RETURNING id', (data_type,))
        if curs.rowcount == 1:
            return curs.fetchone()[0]
        else:
            raise Exception('No row created, or more than one.')

def register_data(data_id, item_id):
    pass

def match_item(item_id, editor, mbid_type, mbid):
    pass
