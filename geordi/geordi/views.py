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
from flask import render_template, request, redirect, url_for, flash, Response, g, json
from flask.ext.login import login_required, login_user, logout_user, current_user
from geordi import app, login_manager, User, es
from geordi.search import do_search, do_search_raw, do_subitem_search, make_filters
from geordi.matching import register_match, check_type
from geordi.mappings import map_search_data, update_map_by_index, update_linked_by_index, get_link_types_by_index, update_automatic_item_matches_by_index, update_automatic_subitem_matches_by_index, get_mapoptions, get_code_url_by_index, get_matching_enabled_by_index
from geordi.mappings.util import comma_list, comma_only_list
from geordi.utils import check_data_format

import uuid
import urllib2
import urllib
import re
import copy
import collections
from datetime import datetime

from pyelasticsearch import ElasticHttpNotFoundError

def dictarray(dictionary):
    return [{'k': i[0], 'v': i[1]} for i in dictionary.iteritems()]

def quote(text):
    return urllib.quote_plus(text.encode('utf-8'))

@app.before_request
def before_request():
    g.all_indices = app.config['AVAILABLE_INDICES']
    g.link_types = dict([(index, get_link_types_by_index(index)) for index in app.config['AVAILABLE_INDICES']])
    g.json = json
    g.re = re
    g.quote = quote
    g.comma_list = comma_list
    g.comma_only_list = comma_only_list
    g.dictarray = dictarray

# Main user-facing views
@app.route('/<itemindex>/<item>')
@login_required
def document(itemindex, item):
    if request.args.get('import', False):
        template = 'import.html'
    else:
        template = 'document.html'
    try:
        data = resolve_data(itemindex, item)
        mapoptions = get_mapoptions(data['_source']['_geordi']['mapping'])
        subitems = {}
        link_types = get_link_types_by_index(itemindex)
        code_url = get_code_url_by_index(itemindex)
        matching_enabled = get_matching_enabled_by_index(itemindex)
        for (link_type, links) in data['_source']['_geordi']['links']['links'].iteritems():
            if link_type != 'version':
                for link in links:
                    subitem = "{}-{}".format(link_type, link[link_types[link_type]['key']])
                    subitems[subitem] = get_subitem(itemindex, subitem, create=True, seed=copy.deepcopy(link))
        return render_template(template, item=item, index=itemindex, data=data, mapping=data['_source']['_geordi']['mapping'], mapoptions=mapoptions, subitems=subitems, code_url=code_url, matching_enabled=matching_enabled)
    except ElasticHttpNotFoundError:
        return render_template('notfound.html')

@app.route('/')
@login_required
def search():
    params = get_search_params()
    if 'error' in params and params['error'] != 'You must provide a query.':
        flash(params["error"])
    return render_template('search.html', query=params.get('query'), data=params.get('data'), mapping=params.get('mapping'), start_from=params.get('start_from'), page_size=params.get('page_size'))

# Internal API urls for matching etc.
@app.route('/api/search')
def apisearch():
    "Perform a search, returning JSON"
    params = get_search_params()
    if 'error' in params:
        response = Response(json.dumps({'code': 400, 'error': params['error']}), 400, mimetype="application/json")
    else:
        response = Response(json.dumps({'code': 200, 'result': params.get('data'), 'mapping': params.get('mapping')}), 200, mimetype="application/json")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

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
        response = Response(json.dumps({'code': 200, 'document': document}), 200, mimetype="application/json")
    except ElasticHttpNotFoundError:
        response = Response(json.dumps({'code': 404, 'error': 'The provided item could not be found.'}), 404, mimetype="application/json")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/matchitem/<index>/<item>')
def matchitem(index, item):
    "Submit a match for this item"
    if get_matching_enabled_by_index(index):
        if current_user.is_authenticated():
            auto = False
            user = None
            if request.args.get('unmatch', False):
                return register_match(index, item, 'item', 'unmatch', [], auto, user)
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
    else:
        return Response(json.dumps({'code': 400, 'error': 'Matching is not enabled for this index'}), 400, mimetype="application/json")

@app.route('/api/subitem/<index>/<subitem>')
def subitem(index, subitem):
    "Get information for a subitem's matching"
    subitem = get_subitem(index, subitem)
    if subitem:
        response = Response(json.dumps({'code': 200, 'document': subitem}), 200, mimetype="application/json")
    else:
        response = Response(json.dumps({'code': 404, 'error': 'The provided item could not be found.'}), 404, mimetype="application/json")
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route('/api/matchsubitem/<index>/<subitem>')
def matchsubitem(index, subitem):
    "Submit a match for this subitem"
    if get_matching_enabled_by_index(index):
        if current_user.is_authenticated():
            auto = False
            user = None
            if request.args.get('unmatch', False):
                return register_match(index, subitem, 'subitem', 'unmatch', [], auto, user)
        else:
            auto = True
            user = request.args.get('user')
        matchtype = request.args.get('type', 'artist')
        mbids = request.args.getlist('mbid')
        if not mbids:
            mbids = re.split(',\s*', request.args.get('mbids'))
        return register_match(index, subitem, 'subitem', matchtype, mbids, auto, user)
    else:
        return Response(json.dumps({'code': 400, 'error': 'Matching is not enabled for this index'}), 400, mimetype="application/json")

@app.route('/internal/mbidtype/<mbid>')
def internal_mbid_type(mbid):
    check = check_type(mbid)
    if 'error' in check:
        return Response(json.dumps({"error": "failed to fetch"}), e.code, mimetype="application/json")
    else:
        return Response(json.dumps(check), 200, mimetype="application/json")

# Login/logout-related views
@app.route('/login')
def login():
    return render_template("login.html", client_id=app.config['OAUTH_CLIENT_ID'], redirect_uri=app.config['OAUTH_REDIRECT_URI'])

@app.route('/internal/oauth')
def oauth_callback():
    error = request.args.get('error')
    if not error:
        state = request.args.getlist('state')
        if len(state) > 0 and state[0] == 'on':
            remember = True
        else:
            remember = False
        code = request.args.get('code')
        username = check_mb_account(code)
        if username:
            login_user(User(username), remember=remember)
            flash("Logged in!")
            return redirect(request.args.get("next") or url_for("search"))
        else:
            flash('We couldn\'t log you in D:')
    else:
        flash('There was an error: ' + error)
    return render_template("login.html", client_id=app.config['OAUTH_CLIENT_ID'], redirect_uri=app.config['OAUTH_REDIRECT_URI'])

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("search"))

# Utilities
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
    search_type = request.args.get('type', 'query')
    start_from = request.args.get('from', "0")
    query = request.args.get('query')
    indices = request.args.getlist('index')
    itemtypes = request.args.getlist('itemtype')
    size = request.args.get('size', None)
    if size is not None:
        size = int(size)
    if size is not None and size == 10:
        size = None

    if len(itemtypes) == 0:
        itemtypes = ['item']

    filters = make_filters(human=request.args.get('human', False), auto=request.args.get('auto', False), un=request.args.get('un', False))

    if search_type == 'raw':
        json_query = json.loads(query)
        if size is None and 'size' in json_query:
            try:
                size = int(json_query['size'])
            except:
                pass
        try:
            data = do_search_raw(json_query, indices, start_from=request.args.get('from', None), filters=filters, doc_type=itemtypes, size=size)
        except ValueError:
            return {'error': "Malformed or missing JSON."}
    elif search_type == 'query':
        if query:
            data = do_search(query, indices, start_from=request.args.get('from', None), filters=filters, doc_type=itemtypes, size=size)
        else:
            return {'error': 'You must provide a query.'}
    elif search_type == 'sub':
        index = request.args.get('subitem_index')
        subtype = request.args.get('subitem_type')
        if subtype not in get_link_types_by_index(index).keys():
            return {'error': 'Invalid subitem type for index {}'.format(index)}
        data = do_subitem_search(query, index, subtype, start_from=request.args.get('from', None), filters=filters, size=size)
    else:
        return {'error': 'Search type {} unimplemented.'.format(search_type)}

    mapping = map_search_data(data)

    return {"start_from": start_from, "query": query, "mapping": mapping, "data": data, "page_size": size}

def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten(el):
                yield sub
        else:
            yield el

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
                    changed = True
                    try:
                        if unicode(seed[key]) not in [unicode(i) for i in data[key]]:
                            data[key].append(seed[key])
                        changed = True
                    except (AttributeError, TypeError):
                        data[key] = list(flatten([data[key], seed[key]]))
                        changed = True
                    if isinstance(data[key], collections.Iterable) and not isinstance(data[key], basestring):
                        data[key] = list(set(flatten(data[key])))
            if changed:
                es.index(index, 'subitem', data, id=subitem)
                document = es.get(index, 'subitem', subitem)
            return document
    except ElasticHttpNotFoundError:
        if create:
            data = check_data_format(seed)
            es.index(index, 'subitem', data, id=subitem)
        return None

def check_mb_account(auth_code):
    url = 'https://musicbrainz.org/oauth2/token'
    data = urllib.urlencode({'grant_type': 'authorization_code',
                             'code': auth_code,
                             'client_id': app.config['OAUTH_CLIENT_ID'],
                             'client_secret': app.config['OAUTH_CLIENT_SECRET'],
                             'redirect_uri': app.config['OAUTH_REDIRECT_URI']})
    json_data = json.load(urllib2.urlopen(url, data))

    url = 'https://beta.musicbrainz.org/oauth2/userinfo'
    opener = urllib2.build_opener()
    opener.addheaders = [('Authorization', 'Bearer ' + json_data['access_token'])]
    try:
        userdata = json.load(opener.open(url, timeout=5))
        return userdata['sub']
    except StandardError:
        return None
