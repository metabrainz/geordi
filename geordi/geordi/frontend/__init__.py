from flask import Blueprint, render_template
from flask.ext.login import login_required
from geordi.db import get_db
import json

frontend = Blueprint('frontend', __name__)

@frontend.route('/login')
def login():
    return 'login? bah'

@frontend.route('/')
def hello_world():
    with get_db().cursor() as curs:
        curs.execute("SELECT 'Hello World!';")
        (v,) = curs.fetchone()
    return render_template('hello.html', hello=v)

@frontend.route('/item/<item_id>')
def item(item_id):
    item = get_item(item_id)
    return render_template('item.html', item=item)

def get_item(item_id):
    data = [{'blah': 'foo', 'baz': {'quux': 'lol'}}]
    return {'id': item_id, 'data': data, 'data_formatted': [json.dumps(d, indent=4) for d in data]}
