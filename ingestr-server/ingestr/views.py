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
from flask import render_template, request, redirect, url_for, flash
from flask.ext.login import login_required, login_user, logout_user, current_user
from ingestr import app, login_manager, User
from ingestr.search import do_search

import json
from pyelasticsearch import ElasticSearch, ElasticHttpNotFoundError

@app.route('/')
def search():
    data = None
    start_from = request.args.get('from', '0')
    if request.args.get('query', False):
        data = do_search(request.args.get('query'), request.args.getlist('index'))
    return render_template('search.html', query = request.args.get('query'), data = data, json = json, start_from = start_from, all_indices = app.config['AVAILABLE_INDICES'], indices = request.args.getlist('index'), current_user = current_user)

@app.route('/<index>/<item>')
def document(index, item):
    es = ElasticSearch(app.config['ELASTICSEARCH_ENDPOINT'])
    try:
        data = es.get(index, 'item', item)
        return render_template('document.html', item=item, index=index, data = data, json = json, all_indices = app.config['AVAILABLE_INDICES'], current_user = current_user)
    except ElasticHttpNotFoundError:
        return render_template('notfound.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST" and "username" in request.form:
        username = request.form["username"]
        login_user(User(username))
        flash("Logged in!")
        return redirect(request.args.get("next") or url_for("search"))
    return render_template("login.html", all_indices = app.config['AVAILABLE_INDICES'], current_user = current_user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("search"))
