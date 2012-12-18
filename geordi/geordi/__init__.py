# geordi
# Copyright (C) 2012 Ian McEwen, MetaBrainz Foundation
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division, absolute_import
from flask import Flask
from flask.ext.login import LoginManager, UserMixin

# CONFIG
SECRET_KEY = 'super seekrit'
ELASTICSEARCH_ENDPOINT = 'http://localhost:9200/'
AVAILABLE_INDICES = ['wcd']

app = Flask(__name__)
app.config.from_object(__name__)
if not app.debug:
    import logging
    from logging.handlers import RotatingFileHandler
    error_filehandler = RotatingFileHandler('/var/log/geordi/errors.log', maxBytes=1024 * 1024 * 10, backupCount=10, encoding='utf_8')
    error_filehandler.setLevel(logging.ERROR)
    warning_filehandler = RotatingFileHandler('/var/log/geordi/warnings.log', maxBytes=1024 * 1024 * 10, backupCount=10, encoding='utf_8')
    warning_filehandler.setLevel(logging.WARNING)
    app.logger.addHandler(error_filehandler)
    app.logger.addHandler(warning_filehandler)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

login_manager = LoginManager()
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(username):
    return User(username)

login_manager.setup_app(app, add_context_processor = True)

import geordi.views
