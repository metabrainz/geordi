from flask import Blueprint, abort, jsonify
from geordi.data.model.item import Item
from geordi.data.model.item_data import ItemData
from geordi.data.mapping.extract import extract_value
import re

api = Blueprint('api', __name__)

@api.route('/item/<int:item_id>')
def item_data(item_id):
    """Get item's data, links, and map.

    :resheader Content-Type: *application/json*
    """
    item = Item.get(item_id)
    if item is None:
        abort(404)
    return jsonify(item.to_dict())

@api.route('/item/<int:item_id>/links')
def item_links(item_id):
    """Get links to specified item.

    :resheader Content-Type: *application/json*
    """
    item = Item.get(item_id)
    if item is None:
        abort(404)

    linked_items = {}
    for item_link in set(item.items_linked):
        linked_items[item_link.item_id] = Item.get(item_link.item_id)

    def to_int_conditionally(val):
        return int(val) if re.match('^\d+$', val) else val

    links = []
    for item_link in item.items_linked:
        path = [to_int_conditionally(x) for x in item_link.type.split('%')]
        links.append(dict(
            item_id=item_link.item_id,
            path=item_link.type,
            value=extract_value(linked_items[item_link.item_id].map_dict, path)[0][1],
        ))

    return jsonify(links=links)

@api.route('/data')
def list_indexes():
    """Get list of indexes.

    :resheader Content-Type: *application/json*
    """
    return jsonify(indexes=ItemData.get_indexes())

@api.route('/data/<index>')
def list_index(index):
    """Get list of item types for a specified index.

    :resheader Content-Type: *application/json*
    """
    item_types = ItemData.get_item_types_by_index(index)
    if not item_types:
        abort(404)
    return jsonify(index=index, item_types=item_types)

@api.route('/data/<index>/<item_type>')
def list_items(index, item_type):
    """Get list of items for a specified index and item type.

    :resheader Content-Type: *application/json*
    """
    item_ids = ItemData.get_item_ids(index, item_type)
    if not item_ids:
        abort(404)
    return jsonify(index=index, item_type=item_type, items=item_ids)

@api.route('/data/<index>/<item_type>/<path:data_id>')
def data_item(index, item_type, data_id):
    """Get item ID based on specified index, item type, and data ID.

    :resheader Content-Type: *application/json*
    """
    item_id = ItemData.data_to_item('/'.join([index, item_type, data_id]))
    if not item_id:
        abort(404)
    return jsonify(index=index, item_type=item_type, data_id=data_id, item_id=item_id)
