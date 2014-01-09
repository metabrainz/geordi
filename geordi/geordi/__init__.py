from __future__ import division, absolute_import
from flask import Flask
from flask.ext.login import LoginManager, UserMixin
from geordi.frontend import frontend
import geordi.settings
import geordi.db as db

class User(UserMixin):
    def __init__(self, id):
        self.id = id

login_manager = LoginManager()
login_manager.login_view = "frontend.login"

@login_manager.user_loader
def load_user(username):
    return User(username)

def create_app():
    app = Flask(__name__)
    app.config.from_object('geordi.settings')
    app.config.from_pyfile('settings.cfg', silent=True)

    login_manager.init_app(app)

    app.register_blueprint(frontend)

    db.init_app(app)

    return app
