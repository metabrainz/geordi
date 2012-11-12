from __future__ import division, absolute_import
from flask import Flask, render_template, request
import json
import urllib2

# CONFIG
SECRET_KEY = 'super seekrit'
DOCUMENT_URL_PATTERN = 'http://localhost:9200/{index}/item/{item}'
SEARCH_URL_PATTERN = 'http://localhost:9200/_search?q={query}'

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def search():
    data = None
    if request.args.get('query', False):
        url = app.config['SEARCH_URL_PATTERN'].format(query = request.args.get('query'))
        req = urllib2.Request(url)
        opener = urllib2.build_opener()
        f = opener.open(req)
        data = json.load(f)
    return render_template('search.html', query = request.args.get('query'), data = data, json = json)

@app.route('/<index>/<item>')
def document(index, item):
    url = app.config['DOCUMENT_URL_PATTERN'].format(index = index, item = item)
    req = urllib2.Request(url)
    opener = urllib2.build_opener()
    f = opener.open(req)
    data = json.load(f)
    return render_template('document.html', item=item, index=index, data = data, json = json)

if __name__ == '__main__':
    app.run(debug = True)
