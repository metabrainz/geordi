from flask import Blueprint, render_template, abort
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
