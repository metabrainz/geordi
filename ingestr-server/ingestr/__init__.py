from __future__ import division, absolute_import
from flask import Flask

# CONFIG
SECRET_KEY = 'super seekrit'
DOCUMENT_URL_PATTERN = 'http://localhost:9200/{index}/item/{item}'
SEARCH_URL_PATTERN = 'http://localhost:9200/_search?q={query}&size=10&from={start_from}'
DB_NAME = 'ingestr'
DB_USER = 'ingestr'
DB_HOST = 'localhost'

app = Flask(__name__)
app.config.from_object(__name__)

import ingestr.views
