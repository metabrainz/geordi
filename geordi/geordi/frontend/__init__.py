from flask import Blueprint
from flask.ext.login import login_required
from geordi.db import get_db

frontend = Blueprint('frontend', __name__)

@frontend.route('/')
def hello_world():
    with get_db().cursor() as curs:
        curs.execute("SELECT 'Hello World!';")
        (v) = curs.fetchone()
    return v

@frontend.route('/login')
def login():
    return 'login? bah'
