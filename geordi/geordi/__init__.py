from __future__ import division, absolute_import
from flask import Flask
from flask.ext.login import LoginManager
from geordi.frontend import frontend
from geordi.api import api
import geordi.settings
from geordi.user import User
from geordi.data.model import db
from geordi.data.model.editor import Editor
import jinja2_highlight
import logging

__version__ = '0.2'

login_manager = LoginManager()
login_manager.login_view = "frontend.homepage"

@login_manager.user_loader
def load_user(username):
    editor = Editor.get(username)
    if editor is not None:
        return User(editor.name, editor.tz)

class GeordiFlask(Flask):
    jinja_options = dict(Flask.jinja_options)
    jinja_options.setdefault('extensions', []).append('jinja2_highlight.HighlightExtension')

def _setup_logger(name, level):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    ch = logging.StreamHandler()
    ch.setLevel(level)
    formatter = logging.Formatter('%(asctime)s (%(levelname)s) %(name)s:  %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def create_app(*args, **kwargs):
    if kwargs.get('log_sql'):
        _setup_logger('sqlalchemy.engine', logging.INFO)
    if kwargs.get('log_debug'):
        _setup_logger('geordi', logging.DEBUG)
    app = GeordiFlask(__name__)
    app.config.from_object('geordi.settings')
    app.config.from_pyfile('settings.cfg', silent=True)

    login_manager.init_app(app)

    app.register_blueprint(frontend)
    app.register_blueprint(api, url_prefix='/api/1')

    db.init_app(app)

    @app.before_first_request
    def setup_logging():
        if not app.debug:
            from logging.handlers import RotatingFileHandler
            if app.config.get('ERROR_LOG'):
                error_fh = RotatingFileHandler(app.config['ERROR_LOG'], maxBytes=1024*1024*10, backupCount=10, encoding='utf_8')
                error_fh.setLevel(logging.ERROR)
                app.logger.addHandler(error_fh)
    return app
