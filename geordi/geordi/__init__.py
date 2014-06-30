from __future__ import division, absolute_import
from flask import Flask
from flask.ext.login import LoginManager
from geordi.frontend import frontend
import geordi.settings
from geordi.user import User
import geordi.db as db
import jinja2_highlight
import logging

login_manager = LoginManager()
login_manager.login_view = "frontend.hello"

@login_manager.user_loader
def load_user(username):
    with db.get_db().cursor() as curs:
        curs.execute('SELECT name, tz FROM editor WHERE name = %s', (username,))
        if curs.rowcount > 0:
            row = curs.fetchone()
            return User(row[0], row[1])

class GeordiFlask(Flask):
    jinja_options = dict(Flask.jinja_options)
    jinja_options.setdefault('extensions', []).append('jinja2_highlight.HighlightExtension')

def create_app(*args, **kwargs):
    if kwargs.get('log_debug'):
        logger = logging.getLogger('geordi')
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s (%(levelname)s) %(name)s:  %(message)s')
        ch.setFormatter(formatter)
        logger.addHandler(ch)
    app = GeordiFlask(__name__)
    app.config.from_object('geordi.settings')
    app.config.from_pyfile('settings.cfg', silent=True)

    login_manager.init_app(app)

    app.register_blueprint(frontend)

    db.init_app(app)

    return app
