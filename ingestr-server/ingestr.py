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
    args = {'url': None, 'data': None}
    if request.args.get('query', False):
        args['url'] = app.config['SEARCH_URL_PATTERN'].format(query = request.args.get('query'))
        req = urllib2.Request(args['url'])
        opener = urllib2.build_opener()
        f = opener.open(req)
        args['data'] = json.load(f)
    print repr(args)
    return render_template('search.html', query = args['url'], data = args['data'])

@app.route('/<index>/<item>')
def document(index, item):
    return render_template('document.html', item=item, index=index)

if __name__ == '__main__':
    app.run(debug = True)
