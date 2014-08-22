"""
geordi.data.model.item_redirect
-------------------------------
"""
from . import db
from .mixins import DeleteMixin


class ItemRedirect(db.Model, DeleteMixin):
    """Model for the 'item_redirect' table, storing the old IDs of items that have been merged."""
    __tablename__ = 'item_redirect'
    __table_args__ = {'schema': 'geordi'}

    #: The obsolete item ID which should be redirected.
    old_id = db.Column('old', db.Integer, primary_key=True)
    #: The item ID to which it should be redirected.
    new_id = db.Column('new', db.Integer, db.ForeignKey('geordi.item.id', ondelete='CASCADE'))
