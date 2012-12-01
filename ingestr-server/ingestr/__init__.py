# ingestr-server
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

# CONFIG
SECRET_KEY = 'super seekrit'
DOCUMENT_URL_PATTERN = 'http://localhost:9200/{index}/item/{item}'
SEARCH_URL_PATTERN = 'http://localhost:9200/_search?q={query}&size=10&from={start_from}'

app = Flask(__name__)
app.config.from_object(__name__)

import ingestr.views
