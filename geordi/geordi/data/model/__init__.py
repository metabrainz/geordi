from sqlalchemy import create_engine
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_tables(app):
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
