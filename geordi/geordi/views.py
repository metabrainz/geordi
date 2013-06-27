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
from flask import render_template, request, redirect, url_for, flash, Response, g, json
from flask.ext.login import login_required, login_user, logout_user
from geordi import app, User
from geordi.matching import check_type
from geordi.mappings import get_link_types_by_index, get_mapoptions, get_code_url_by_index, get_matching_enabled_by_index
from geordi.mappings.util import comma_list, comma_only_list
from geordi.data import resolve_data, get_search_params, get_subitem

from geordi.api import bp as api

import urllib2
import urllib
import copy

from pyelasticsearch import ElasticHttpNotFoundError

app.register_blueprint(api)

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

# Internal lookup for MBIDs for the UI
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
