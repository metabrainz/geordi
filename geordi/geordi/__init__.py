from __future__ import division, absolute_import
from flask import Flask
from flask.ext.login import LoginManager
from geordi.frontend import frontend
import geordi.settings
from geordi.user import User
from geordi.data.model import db
from geordi.data.model.editor import Editor
import jinja2_highlight
import logging

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

    @app.before_first_request
    def setup_logging():
        if not app.debug:
            from logging.handlers import RotatingFileHandler
            if app.config.get('ERROR_LOG'):
                error_fh = RotatingFileHandler(app.config['ERROR_LOG'], maxBytes=1024*1024*10, backupCount=10, encoding='utf_8')
                error_fh.setLevel(logging.ERROR)
                app.logger.addHandler(error_fh)
    return app
