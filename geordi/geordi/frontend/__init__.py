from flask import Blueprint, render_template, abort, redirect, url_for
from ..db import get_db
import geordi.data as data
import json

frontend = Blueprint('frontend', __name__)

@frontend.route('/login')
def login():
    return 'login unimplemented yet'

@frontend.route('/')
def hello():
    return render_template('hello.html')

@frontend.route('/item/<item_id>')
def item(item_id):
    item = data.get_renderable(item_id)
    if item is None:
        abort(404)
    return render_template('item.html', item=item)

@frontend.route('/data/<index>/<item_type>/<data_id>')
def data_item(index, item_type, data_id):
    item_id = data.data_to_item('/'.join([index, item_type, data_id]))
    if item_id is None:
        abort(404)
    else:
        return redirect(url_for('.item', item_id=item_id))
