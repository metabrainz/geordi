from __future__ import division, absolute_import
from flask import render_template, request
from ingestr import app

import json
from pyelasticsearch import ElasticSearch

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
    data = es.get(index, 'item', item)
    return render_template('document.html', item=item, index=index, data = data, json = json)
