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
from ingestr.search import do_search

import json
import uuid
import urllib2
from datetime import datetime

from pyelasticsearch import ElasticSearch, ElasticHttpNotFoundError

es = ElasticSearch(app.config['ELASTICSEARCH_ENDPOINT'])

@app.before_request
def before_request():
    g.all_indices = app.config['AVAILABLE_INDICES']

# Main user-facing views
@app.route('/')
def search():
    data = None
    if request.args.get('query', False):
        data = do_search(request.args.get('query'), request.args.getlist('index'), start_from=request.args.get('from', None))
    return render_template('search.html', query=request.args.get('query'), data = data, start_from=request.args.get('from', '0'))

@app.route('/<index>/<item>')
def document(index, item):
    try:
        data = es.get(index, 'item', item)
        return render_template('document.html', item=item, index=index, data = data)
    except ElasticHttpNotFoundError:
        return render_template('notfound.html')

# Internal API urls for matching etc.
@app.route('/api/matchitem/<index>/<item>')
@login_required
def matchitem(index, item):
    "Submit a match for this item"
    matchtype = request.args.get('type', 'release')
    mbid = request.args.get('mbid', None)
    return register_match(index, item, 'item', matchtype, mbid)

@app.route('/api/subitem/<index>/<subitem>')
def subitem(index, subitem):
    "Get information for a subitem's matching"
    document = es.get(index, 'subitem', subitem)

    return Response(json.dumps({'code': 500, 'error': 'Not Implemented.', 'document': document}), 500)

@app.route('/api/matchsubitem/<index>/<subitem>')
@login_required
def matchsubitem(index, subitem):
    "Submit a match for this subitem"
    matchtype = request.args.get('type', 'artist')
    mbid = request.args.get('mbid', None)
    return register_match(index, subitem, 'subitem', matchtype, mbid)

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

# Utility functions
def make_match_definition(user, matchtype, mbid):
    return {'user': user,
         'timestamp': datetime.utcnow(),
         'type': matchtype,
         'mbid': mbid}

def register_match(index, item, itemtype, matchtype, mbid):
    if not mbid:
        return Response(json.dumps({'code': 400, 'error': 'You must provide an MBID for a match.'}), 400)
    # Check MBID formatting
    try:
        uuid.UUID('{{{uuid}}}'.format(uuid=mbid))
    except ValueError:
        return Response(json.dumps({'code': 400, 'error': 'The provided MBID is ill-formed'}), 400)
    # Retrieve document (or blank empty document for subitems)
    try:
        document = es.get(index, itemtype, item)
        data = document['_source']
        version = document['_version']
    except ElasticHttpNotFoundError:
        if itemtype == 'item':
            return Response(json.dumps({'code': 404, 'error': 'The provided item could not be found.'}), 404)
        else:
            data = {}
            version = None

    if '_ingestr' not in data:
        data['_ingestr'] = {}
    if 'matchings' not in data['_ingestr']:
        data['_ingestr']['matchings'] = []

    data['_ingestr']['matchings'].append(make_match_definition(current_user.id, matchtype, mbid))

    try:
        if version:
            es.index(index, itemtype, data, id=item, es_version=version)
        else:
            es.index(index, itemtype, data, id=item)
        return Response(json.dumps({'code': 200}), 200)
    except:
        return Response(json.dumps({'code': 500, 'error': 'An unknown error happened while pushing to elasticsearch.'}), 500)

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
