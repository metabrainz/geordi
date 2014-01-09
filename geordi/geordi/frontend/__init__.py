from flask import Blueprint
from flask.ext.login import login_required

frontend = Blueprint('frontend', __name__)

@frontend.route('/')
@login_required
def hello_world():
    return 'Hello World!'

@frontend.route('/login')
def login():
    return 'login? bah'
