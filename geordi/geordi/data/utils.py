from ..db import get_db
import json

def get_item(item_id):
    data = [{'blah': 'foo', 'baz': {'quux': 'lol'}}]
    return {'id': item_id, 'data': data}

def get_renderable(item_id):
    item = get_item(item_id)
    item['data_formatted'] = [json.dumps(i, indent=4) for i in item.get('data', [])]
    return item

def add_data(data_id, data_type, data):
    pass

def data_to_item(data_id):
    pass

def map_item(item_id):
    pass

def create_item(data_type):
    pass

def register_data(data_id, item_id):
    pass

def match_item():
    pass
