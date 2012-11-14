from __future__ import division, absolute_import
from flask import Flask, render_template, request
import json
import urllib2
import urllib

# CONFIG
SECRET_KEY = 'super seekrit'
DOCUMENT_URL_PATTERN = 'http://localhost:9200/{index}/item/{item}'
SEARCH_URL_PATTERN = 'http://localhost:9200/_search?q={query}&size=10&from={start_from}'

app = Flask(__name__)
app.config.from_object(__name__)

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

if __name__ == '__main__':
    app.run(debug = True)
