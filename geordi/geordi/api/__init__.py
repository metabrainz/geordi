from flask import Blueprint, abort, jsonify
from geordi.data.model.item_data import ItemData

api = Blueprint('api', __name__)

@api.route('/item/<item_id>')
def item_data(item_id):
    raise NotImplementedError

@api.route('/item/<item_id>/map')
def item_map(item_id):
    raise NotImplementedError

@api.route('/data')
def list_indexes():
    return jsonify(indexes=ItemData.get_indexes())

@api.route('/data/<index>')
def list_index(index):
    return jsonify(index=index, item_types=ItemData.get_item_types_by_index(index))

@api.route('/data/<index>/<item_type>')
def list_items(index, item_type):
    return jsonify(index=index, item_type=item_type, items=ItemData.get_item_ids(index, item_type))

@api.route('/data/<index>/<item_type>/<data_id>')
def data_item(index, item_type, data_id):
    item_id = ItemData.data_to_item('/'.join([index, item_type, data_id]))
    if item_id is None:
        abort(404)
    else:
        return jsonify(index=index, item_type=item_type, data_id=data_id, item_id=item_id)
