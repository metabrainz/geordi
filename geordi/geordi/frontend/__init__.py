from flask import Blueprint, render_template
from geordi.db import get_db
import geordi.data as data
import json

frontend = Blueprint('frontend', __name__)

@frontend.route('/login')
def login():
    return 'login unimplemented yet'

@frontend.route('/')
def hello_world():
    with get_db().cursor() as curs:
        curs.execute("SELECT 'Hello World!';")
        (v,) = curs.fetchone()
    return render_template('hello.html', hello=v)

@frontend.route('/item/<item_id>')
def item(item_id):
    item = data.get_renderable(item_id)
    return render_template('item.html', item=item)
