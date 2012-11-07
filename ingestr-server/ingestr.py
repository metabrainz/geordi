from __future__ import division, absolute_import
from flask import Flask, render_template, request

# CONFIG
SECRET_KEY = 'super seekrit'

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<index>/<item>')
def document(index, item):
    return render_template('document.html', item=item, index=index)

@app.route('/search')
def search():
    return render_template('search.html', query = request.args.get('query'))

if __name__ == '__main__':
    app.run(debug = True)
