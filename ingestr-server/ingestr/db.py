from __future__ import division, absolute_import
from ingestr import app

import psycopg2

def get_conn():
    try:
        return psycopg2.connect("dbname='{dbname}' user='{dbuser}' host='{dbhost}'".format(dbname = app.config['DB_NAME'], dbuser = app.config['DB_USER'], dbhost = app.config['DB_HOST']))
    except:
        return None
