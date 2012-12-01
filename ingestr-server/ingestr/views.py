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
from flask import render_template, request
from ingestr import app

import json
from pyelasticsearch import ElasticSearch, ElasticHttpNotFoundError

@app.route('/')
def search():
    data = None
    start_from = request.args.get('from', '0')
    if request.args.get('query', False):
        es = ElasticSearch('http://localhost:9200/')
        data = es.search({'query': {'bool': {'must': [{"query_string":{"query":request.args.get('query')}}]}}})
    return render_template('search.html', query = request.args.get('query'), data = data, json = json, start_from = start_from)

@app.route('/<index>/<item>')
def document(index, item):
    es = ElasticSearch('http://localhost:9200/')
    try:
        data = es.get(index, 'item', item)
        return render_template('document.html', item=item, index=index, data = data, json = json)
    except ElasticHttpNotFoundError:
        return render_template('notfound.html')
