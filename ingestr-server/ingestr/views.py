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
from flask.ext.login import login_required, login_user, logout_user
from ingestr import app, login_manager, User
from ingestr.search import do_search

import json
import uuid
import urllib2

from pyelasticsearch import ElasticSearch, ElasticHttpNotFoundError

@app.before_request
def before_request():
    g.all_indices = app.config['AVAILABLE_INDICES']

# Main user-facing views
@app.route('/')
def search():
    data = None
    start_from = request.args.get('from', '0')
    if request.args.get('query', False):
        data = do_search(request.args.get('query'), request.args.getlist('index'), start_from=start_from)
    return render_template('search.html', query = request.args.get('query'), data = data, start_from = start_from, indices = request.args.getlist('index'))

@app.route('/<index>/<item>')
def document(index, item):
    es = ElasticSearch(app.config['ELASTICSEARCH_ENDPOINT'])
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
    if not mbid:
        return Response(json.dumps({'code': 400, 'error': 'You must provide an MBID for a match.'}), 400)
    try:
        uuid.UUID('{{{uuid}}}'.format(uuid=mbid))
    except ValueError:
        return Response(json.dumps({'code': 400, 'error': 'The provided MBID is ill-formed'}), 400)

    pass

@app.route('/api/subitem/<index>/<subitem>')
def subitem(index, subitem):
    "Get information for a subitem's matching"
    pass

@app.route('/api/matchsubitem/<index>/<subitem>')
@login_required
def matchsubitem(index, subitem):
    "Submit a match for this subitem"
    matchtype = request.args.get('type', 'release')
    mbid = request.args.get('mbid', None)
    if not mbid:
        return Response(json.dumps({'code': 400, 'error': 'You must provide an MBID for a match.'}), 400)
    try:
        uuid.UUID('{{{uuid}}}'.format(uuid=mbid))
    except ValueError:
        return Response(json.dumps({'code': 400, 'error': 'The provided MBID is ill-formed'}), 400)

    pass

# Login/logout-related views
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST" and "username" in request.form:
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
