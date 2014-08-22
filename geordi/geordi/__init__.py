from __future__ import division, absolute_import
from flask import Flask
from flask.ext.login import LoginManager
from geordi.frontend.views import frontend as frontend_bp
from geordi.api.views import api as api_bp
from geordi import errors
from geordi.user import User
from geordi.data.model import db
from geordi.data.model.editor import Editor
import geordi.base_settings
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

def create_app(settings_file='settings.cfg', *args, **kwargs):
    app = GeordiFlask(__name__)
    errors.init_error_handlers(app)

    # Logging
    if kwargs.get('log_sql'):
        _setup_logger('sqlalchemy.engine', logging.INFO)
    if kwargs.get('log_debug'):
        _setup_logger('geordi', logging.DEBUG)

    # Config
    app.config.from_object(geordi.base_settings)
    app.config.from_pyfile(settings_file, silent=True)

    # Extensions
    db.init_app(app)
    login_manager.init_app(app)

    # Blueprints
    app.register_blueprint(frontend_bp)
    app.register_blueprint(api_bp, url_prefix='/api/1')

    @app.before_first_request
    def setup_logging():
        if not app.debug:
            from logging.handlers import RotatingFileHandler
            if app.config.get('ERROR_LOG'):
                error_fh = RotatingFileHandler(app.config['ERROR_LOG'], maxBytes=1024*1024*10, backupCount=10, encoding='utf_8')
                error_fh.setLevel(logging.ERROR)
                app.logger.addHandler(error_fh)

    return app
