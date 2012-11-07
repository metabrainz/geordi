from __future__ import division, absolute_import
from flask import Flask, render_template, request

# CONFIG
SECRET_KEY = 'super seekrit'

app = Flask(__name__)
app.config.from_object(__name__)

@app.route('/')
def search():
    return render_template('search.html', query = request.args.get('query'))

@app.route('/<index>/<item>')
def document(index, item):
    return render_template('document.html', item=item, index=index)

if __name__ == '__main__':
    app.run(debug = True)
