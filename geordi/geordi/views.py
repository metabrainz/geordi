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
from flask import render_template, request, redirect, url_for, flash, Response, g
from flask.ext.login import login_required, login_user, logout_user, current_user
from geordi import app, login_manager, User, es
from geordi.search import do_search, do_search_raw, do_subitem_search, make_filters
from geordi.matching import register_match
from geordi.mappings import map_search_data, update_map_by_index, update_linked_by_index, get_link_types_by_index, update_automatic_item_matches_by_index, update_automatic_subitem_matches_by_index, get_mapoptions, get_code_url_by_index
from geordi.mappings.util import comma_list, comma_only_list
from geordi.utils import check_data_format

import json
import uuid
import urllib2
import re
import copy
from datetime import datetime

from pyelasticsearch import ElasticHttpNotFoundError

def dictarray(dictionary):
    return [{'k': i[0], 'v': i[1]} for i in dictionary.iteritems()]

@app.before_request
def before_request():
    g.all_indices = app.config['AVAILABLE_INDICES']
    g.link_types = dict([(index, get_link_types_by_index(index)) for index in app.config['AVAILABLE_INDICES']])
    g.json = json
    g.comma_list = comma_list
    g.comma_only_list = comma_only_list
    g.dictarray = dictarray

# Main user-facing views
@app.route('/<index>/<item>')
@login_required
def document(index, item):
    try:
        data = resolve_data(index, item)
        mapoptions = get_mapoptions(data['_source']['_geordi']['mapping'])
        subitems = {}
        link_types = get_link_types_by_index(index)
        code_url = get_code_url_by_index(index)
        for (link_type, links) in data['_source']['_geordi']['links']['links'].iteritems():
            if link_type != 'version':
                for link in links:
                    subitem = "{}-{}".format(link_type, link[link_types[link_type]['key']])
                    subitems[subitem] = get_subitem(index, subitem, create=True, seed=copy.deepcopy(link))
        return render_template('document.html', item=item, index=index, data = data, mapping = data['_source']['_geordi']['mapping'], mapoptions = mapoptions, subitems=subitems, code_url=code_url)
    except ElasticHttpNotFoundError:
        return render_template('notfound.html')

def resolve_data(index, item):
    "Shared data-update functionality"
    data = es.get(index, 'item', item)
    linked_update = update_linked_by_index(index, item, data['_source'])
    map_update = update_map_by_index(index, item, data['_source'])
    match_update = update_automatic_item_matches_by_index(index, item, data['_source'])
    if linked_update or map_update or match_update:
        data = es.get(index, 'item', item)
    update_automatic_subitem_matches_by_index(index, item, data['_source'])
    return data

def get_search_params():
    "Shared search functionality"
    search_type = request.args.get('type', 'item')
    start_from = request.args.get('from', "0")
    query = request.args.get('query')
    indices = request.args.getlist('index')
    itemtype = 'item'

    filters = make_filters(human=request.args.get('human', False), auto=request.args.get('auto', False), un=request.args.get('un', False))

    if search_type == 'raw':
        try:
            data = do_search_raw(json.loads(query), indices, start_from=request.args.get('from', None), filters=filters)
        except ValueError:
            return {'error': "Malformed or missing JSON."}
    elif search_type == 'item':
        if query:
            data = do_search(query, indices, start_from=request.args.get('from', None), filters=filters)
        else:
            return {'error': 'You must provide a query.'}
    elif search_type == 'sub':
        index = request.args.get('subitem_index')
        subtype = request.args.get('subitem_type')
        if subtype not in get_link_types_by_index(index).keys():
            return {'error': 'Invalid subitem type for index {}'.format(index)}
        data = do_subitem_search(query, index, subtype, start_from=request.args.get('from', None), filters=filters)
    elif search_type == 'subitem':
        if query:
            data = do_search(query, indices, start_from=request.args.get('from', None), filters=filters, doc_type='subitem')
            itemtype = 'subitem'
        else:
            return {'error': 'You must provide a query.'}
    elif search_type == 'raw-subitem':
        try:
            data = do_search_raw(json.loads(query), indices, start_from=request.args.get('from', None), filters=filters, doc_type='subitem')
            itemtype = 'subitem'
        except ValueError:
            return {'error': "Malformed or missing JSON."}
    else:
        return {'error': 'Search type {} unimplemented.'.format(search_type)}

    if itemtype == 'item':
        mapping = map_search_data(data)
    elif itemtype == 'subitem':
        mapping = [re.split('-', item['_id'], maxsplit=0) for item in data['hits']['hits']]

    return {"start_from": start_from, "query": query, "mapping": mapping, "data": data}

@app.route('/')
@login_required
def search():
    params = get_search_params()
    if 'error' in params and params['error'] != 'You must provide a query.':
        flash(params["error"])
    return render_template('search.html', query=params.get('query'), data = params.get('data'), mapping = params.get('mapping'), start_from= params.get('start_from'))

# Internal API urls for matching etc.
@app.route('/api/search')
def apisearch():
    "Perform a search, returning JSON"
    params = get_search_params()
    if 'error' in params:
        return Response(json.dumps({'code': 400, 'error': params['error']}), 400, mimetype="application/json")
    return Response(json.dumps({'code': 200, 'result': params.get('data'), 'mapping': params.get('mapping')}), 200, mimetype="application/json");

@app.route('/api/item/<index>/<item>')
def item(index, item):
    "Get information for an item"
    try:
        document = resolve_data(index, item)
        if request.args.get('subitems', False):
            link_types = get_link_types_by_index(index)
            for (link_type, links) in document['_source']['_geordi']['links']['links'].iteritems():
                if link_type != 'version':
                    for link in links:
                        subitem = "{}-{}".format(link_type, link[link_types[link_type]['key']])
                        get_subitem(index, subitem, create=True, seed=copy.deepcopy(link))
        return Response(json.dumps({'code': 200, 'document': document}), 200, mimetype="application/json");
    except ElasticHttpNotFoundError:
        return Response(json.dumps({'code': 404, 'error': 'The provided item could not be found.'}), 404, mimetype="application/json")

@app.route('/api/matchitem/<index>/<item>')
def matchitem(index, item):
    "Submit a match for this item"
    if current_user.is_authenticated():
        auto = False
        user = None
    else:
        auto = True
        user = request.args.get('user')
        if user in ['matched by index']:
            return Response(json.dumps({'code': 400, 'error': 'The name "{}" is reserved.'.format(user)}), 400, mimetype="application/json")
    matchtype = request.args.get('type', 'release')
    mbids = request.args.getlist('mbid')
    if not mbids:
        mbids = re.split(',\s*', request.args.get('mbids'))
    return register_match(index, item, 'item', matchtype, mbids, auto, user)

def get_subitem(index, subitem, create=False, seed={}):
    try:
        document = es.get(index, 'subitem', subitem)
        if seed == {}:
            return document
        else:
            data = document['_source']
            data = check_data_format(data)
            changed = False
            for key in seed.keys():
                if key not in data:
                    data[key] = seed[key]
                    changed = True
                elif key in data:
                    try:
                        if unicode(seed[key]) not in [unicode(i) for i in data[key]]:
                            data[key].append(seed[key])
                        changed = True
                    except (AttributeError, TypeError):
                        data[key] = [data[key], seed[key]]
                        changed = True
            if changed:
                es.index(index, 'subitem', data, id=subitem)
                document = es.get(index, 'subitem', subitem)
            return document
    except ElasticHttpNotFoundError:
        if create:
            data = check_data_format(seed)
            es.index(index, 'subitem', data, id=subitem)
        return None

@app.route('/api/subitem/<index>/<subitem>')
def subitem(index, subitem):
    "Get information for a subitem's matching"
    subitem = get_subitem(index, subitem)
    if subitem:
        return Response(json.dumps({'code': 200, 'document': subitem}), 200, mimetype="application/json");
    else:
        return Response(json.dumps({'code': 404, 'error': 'The provided item could not be found.'}), 404, mimetype="application/json")

@app.route('/api/matchsubitem/<index>/<subitem>')
def matchsubitem(index, subitem):
    "Submit a match for this subitem"
    if current_user.is_authenticated():
        auto = False
        user = None
    else:
        auto = True
        user = request.args.get('user')
    matchtype = request.args.get('type', 'artist')
    mbids = request.args.getlist('mbid')
    if not mbids:
        mbids = re.split(',\s*', request.args.get('mbids'))
    return register_match(index, subitem, 'subitem', matchtype, mbids, auto, user)

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
    opener.addheaders = [('User-Agent', 'Geordi-Login +http://geordi.musicbrainz.org/login')]
    try:
        opener.open(url, timeout=5)
    except StandardError:
        return False
    return True
