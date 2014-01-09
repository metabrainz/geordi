# geordi
# Copyright (C) 2012-2013 Ian McEwen, MetaBrainz Foundation
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
from flask import g, json
from geordi import app
from geordi.mappings import get_index
from geordi.mappings.util import comma_list, comma_only_list

from geordi.api import bp as api
from geordi.ui import bp as ui

import urllib
import re

app.register_blueprint(api)
app.register_blueprint(ui)

def dictarray(dictionary):
    return [{'k': i[0], 'v': i[1]} for i in dictionary.iteritems()]

def quote(text):
    return urllib.quote_plus(text.encode('utf-8'))

@app.before_request
def before_request():
    g.all_indices = app.config['AVAILABLE_INDICES']
    g.link_types = dict([(index, get_index(index).link_types()) for index in app.config['AVAILABLE_INDICES']])
    g.json = json
    g.re = re
    g.quote = quote
    g.comma_list = comma_list
    g.comma_only_list = comma_only_list
    g.dictarray = dictarray
