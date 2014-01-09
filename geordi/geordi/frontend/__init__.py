from flask import Blueprint, render_template
from flask.ext.login import login_required
from geordi.db import get_db

frontend = Blueprint('frontend', __name__)

@frontend.route('/')
def hello_world():
    with get_db().cursor() as curs:
        curs.execute("SELECT 'Hello World!';")
        (v,) = curs.fetchone()
    return render_template('hello.html', hello=v)

@frontend.route('/login')
def login():
    return 'login? bah'
