"""
geordi.data.model
-----------------

Geordi model grouping module and general database-management tools.
"""
from sqlalchemy import create_engine
from flask.ext.sqlalchemy import SQLAlchemy

#: A shared SQLAlchemy object for use across geordi.
#: Intended to be imported from views, models, etc.
db = SQLAlchemy()


def create_tables(app):
    '''Initialize tables in the database. Assumes the database already exists and a 'geordi' schema is created.'''
    engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
    db.metadata.create_all(engine)
    return engine

from .csrf import CSRF
from .editor import Editor
from .item import Item
from .item_data import ItemData
from .item_redirect import ItemRedirect
from .item_link import ItemLink
from .entity import Entity
from .raw_match import RawMatch
from .raw_match_entity import RawMatchEntity
