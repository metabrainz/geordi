from __future__ import division, absolute_import
from flask import render_template, request
from ingestr import app
from ingestr.db import get_conn

import json
import urllib2
import urllib

@app.route('/')
def search():
    data = None
    start_from = request.args.get('from', '0')
    if request.args.get('query', False):
        url = app.config['SEARCH_URL_PATTERN'].format(query = urllib.quote_plus(request.args.get('query')),
                                                      start_from = urllib.quote_plus(start_from))
        req = urllib2.Request(url)
        opener = urllib2.build_opener()
        f = opener.open(req)
        data = json.load(f)
    return render_template('search.html', query = request.args.get('query'), data = data, json = json, start_from = start_from)

@app.route('/<index>/<item>')
def document(index, item):
    url = app.config['DOCUMENT_URL_PATTERN'].format(index = index, item = item)
    req = urllib2.Request(url)
    opener = urllib2.build_opener()
    f = opener.open(req)
    data = json.load(f)
    return render_template('document.html', item=item, index=index, data = data, json = json)

@app.route('/dbinfo')
def dbinfo():
    ret = ""
    conn = get_conn()
    if conn is None:
        return "failed to connect"
    else:
        ret = ret + "connected to postgres\n"

    cur = conn.cursor()
    cur.execute("SELECT table_name, column_name, column_default, data_type from information_schema.columns where table_schema = 'public'")
    rows = cur.fetchall()
    ret = ret + repr(rows)

    return ret
