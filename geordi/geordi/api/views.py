from flask import Blueprint, abort, jsonify
from geordi.data.model import db
from geordi.data.model.item import Item
from geordi.data.model.item_data import ItemData
from geordi.data.model.raw_match import RawMatch

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
    item = Item.query.filter_by(id=item_id).options(db.joinedload('items_linked').joinedload('item')).first()
    if item is None:
        abort(404)
    links = []
    for item_link in item.items_linked:
        links.append(dict(
            item_id=item_link.item_id,
            path=item_link.type,
            value=item_link.value,
        ))
    return jsonify(links=links)

@api.route('/item/<int:item_id>/matches')
def item_matches(item_id):
    current = RawMatch.get_by_item(item_id, superseded=False)
    previous = RawMatch.get_by_item(item_id, superseded=True)
    return jsonify({
        'matches': {
            'current': current[0].to_dict() if current else None,
            'superseded': [match.to_dict() for match in previous]
        }
    })

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
