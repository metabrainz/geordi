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
from flask import render_template, request, redirect, url_for, flash, Response, g
from flask.ext.login import login_required, login_user, logout_user, current_user
from ingestr import app, login_manager, User
from ingestr.search import do_search, do_search_raw
from ingestr.matching import register_match
from ingestr.mappings import map_search_data, map_by_index, update_linked_by_index, get_link_types_by_index, get_mapoptions
from ingestr.mappings.util import comma_list, comma_only_list

import json
import uuid
import urllib2
from datetime import datetime

from pyelasticsearch import ElasticSearch, ElasticHttpNotFoundError

es = ElasticSearch(app.config['ELASTICSEARCH_ENDPOINT'])

def dictarray(dictionary):
    return [{'k': i[0], 'v': i[1]} for i in dictionary.iteritems()]

@app.before_request
def before_request():
    g.all_indices = app.config['AVAILABLE_INDICES']
    g.json = json
    g.comma_list = comma_list
    g.comma_only_list = comma_only_list
    g.dictarray = dictarray

# Main user-facing views
@app.route('/')
def search():
    data = None
    mapping = None
    if request.args.get('query', False):
        data = do_search(request.args.get('query'), request.args.getlist('index'), start_from=request.args.get('from', None))
        mapping = map_search_data(data)
    return render_template('search.html', query=request.args.get('query'), data = data, mapping = mapping, start_from=request.args.get('from', '0'))

@app.route('/<index>/<item>')
def document(index, item):
    try:
        data = es.get(index, 'item', item)
        if update_linked_by_index(index, item, data['_source']):
            data = es.get(index, 'item', item)
        mapping = map_by_index(index, data['_source'])
        link_types = get_link_types_by_index(index)
        mapoptions = get_mapoptions(mapping)
        return render_template('document.html', item=item, index=index, data = data, mapping = mapping, link_types = link_types, mapoptions = mapoptions)
    except ElasticHttpNotFoundError:
        return render_template('notfound.html')

# Internal API urls for matching etc.
@app.route('/api/search', methods=["GET", "POST"])
def apisearch():
    "Perform a search, returning JSON"
    if request.method == "POST":
        query = request.form['query']
        indices = request.form['index'].split(',')
        try:
            json.loads(query)
        except ValueError:
            return Response(json.dumps({'code': 400, 'error': 'JSON raw query is malformed or missing.'}), 400, mimetype="application/json")

        data = do_search_raw(query, indices)
        mapping = map_search_data(data)
        return Response(json.dumps({'code': 200, 'result': data, 'mapping': mapping}), 200, mimetype="application/json");
    else:
        if request.args.get('query', False):
            data = do_search(request.args.get('query'), request.args.getlist('index'), start_from=request.args.get('from', None))
            mapping = map_search_data(data)
            return Response(json.dumps({'code': 200, 'result': data, 'mapping': mapping}), 200, mimetype="application/json");
        else:
            return Response(json.dumps({'code': 400, 'error': 'You must provide a query string.'}), 400, mimetype="application/json")

@app.route('/api/item/<index>/<subitem>')
def item(index, item):
    "Get information for an item"
    try:
        document = es.get(index, 'item', item)
        return Response(json.dumps({'code': 200, 'document': document}), 200, mimetype="application/json");
    except ElasticHttpNotFoundError:
        return Response(json.dumps({'code': 404, 'error': 'The provided item could not be found.'}), 404, mimetype="application/json")

@app.route('/api/matchitem/<index>/<item>')
@login_required
def matchitem(index, item):
    "Submit a match for this item"
    matchtype = request.args.get('type', 'release')
    mbids = request.args.getlist('mbid')
    return register_match(index, item, 'item', matchtype, mbids)

@app.route('/api/subitem/<index>/<subitem>')
def subitem(index, subitem):
    "Get information for a subitem's matching"
    try:
        document = es.get(index, 'subitem', subitem)
        return Response(json.dumps({'code': 200, 'document': document}), 200, mimetype="application/json");
    except ElasticHttpNotFoundError:
        return Response(json.dumps({'code': 404, 'error': 'The provided item could not be found.'}), 404, mimetype="application/json")

@app.route('/api/matchsubitem/<index>/<subitem>')
@login_required
def matchsubitem(index, subitem):
    "Submit a match for this subitem"
    matchtype = request.args.get('type', 'artist')
    mbids = request.args.getlist('mbid')
    return register_match(index, subitem, 'subitem', matchtype, mbids)

# Login/logout-related views
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username and password:
            if check_mb_account(username, password):
                login_user(User(username))
                flash("Logged in!")
                return redirect(request.args.get("next") or url_for("search"))
            else:
                flash('Invalid username or password.')
        else:
            flash('You must provide a username and password.')
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("search"))

# What follows, until the end of the file, is shamelessly cribbed from acoustid-server
class DigestAuthHandler(urllib2.HTTPDigestAuthHandler):
    """Patched DigestAuthHandler to correctly handle Digest Auth according to RFC 2617.

    This will allow multiple qop values in the WWW-Authenticate header (e.g. "auth,auth-int").
    The only supported qop value is still auth, though.
    See http://bugs.python.org/issue9714

    @author Kuno Woudt
    """
    def get_authorization(self, req, chal):
        qop = chal.get('qop')
        if qop and ',' in qop and 'auth' in qop.split(','):
            chal['qop'] = 'auth'
        return urllib2.HTTPDigestAuthHandler.get_authorization(self, req, chal)

def check_mb_account(username, password):
    url = 'https://musicbrainz.org/ws/2/artist/89ad4ac3-39f7-470e-963a-56509c546377?inc=user-tags'
    auth_handler = DigestAuthHandler()
    auth_handler.add_password('musicbrainz.org', 'https://musicbrainz.org/',
                              username.encode('utf8'), password.encode('utf8'))
    opener = urllib2.build_opener(auth_handler)
    opener.addheaders = [('User-Agent', 'Ingestr-Login +http://ingestr.musicbrainz.org/login')]
    try:
        opener.open(url, timeout=5)
    except StandardError:
        return False
    return True
