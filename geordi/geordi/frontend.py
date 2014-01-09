from flask import Blueprint

frontend = Blueprint('frontend', __name__)

@frontend.route('/')
def hello_world():
    return 'Hello World!'
