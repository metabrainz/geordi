from __future__ import division, absolute_import
from flask import Flask
from flask.ext.login import LoginManager, UserMixin
from geordi.frontend import frontend
import geordi.settings
import geordi.db as db
import jinja2_highlight

class User(UserMixin):
    def __init__(self, id):
        self.id = id

login_manager = LoginManager()
login_manager.login_view = "frontend.login"

@login_manager.user_loader
def load_user(username):
    return User(username)

class GeordiFlask(Flask):
    jinja_options = dict(Flask.jinja_options)
    jinja_options.setdefault('extensions', []).append('jinja2_highlight.HighlightExtension')

def create_app():
    app = GeordiFlask(__name__)
    app.config.from_object('geordi.settings')
    app.config.from_pyfile('settings.cfg', silent=True)

    login_manager.init_app(app)

    app.register_blueprint(frontend)

    db.init_app(app)

    return app
