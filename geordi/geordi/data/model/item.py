"""
geordi.data.model.item
----------------------
"""
from . import db
from .mixins import DeleteMixin
import json


class Item(db.Model, DeleteMixin):
    """Model for the 'item' table, storing item type information and mapped data."""
    __tablename__ = 'item'
    __table_args__ = {'schema': 'geordi'}

    #: Integer ID of this item.
    id = db.Column(db.Integer, primary_key=True)
    #: Nominal type guess for this item.
    type = db.Column(db.Unicode)
    #: Mapped data for this item, JSON.
    map = db.Column(db.UnicodeText)

    #: Property for data items linked to this item. Included by default when loading.
    item_data = db.relationship('ItemData', lazy='joined', cascade='delete', backref='item')
    #: Property for redirects to this item.
    item_redirects = db.relationship('ItemRedirect', cascade='delete', backref='new')

    # Item links
    #: Property for links from this item to other items. Included by default when loading.
    item_links = db.relationship('ItemLink', lazy='joined', cascade='delete', backref='item', foreign_keys='ItemLink.item_id')
    #: Property for links from other items to this item. Not loaded by default.
    items_linked = db.relationship('ItemLink', cascade='delete', backref='linked', foreign_keys='ItemLink.linked_id')

    # Matches
    #: Property for matches of this item to MusicBrainz entities.
    raw_matches = db.relationship('RawMatch', cascade='delete', backref='item')

    @property
    def map_dict(self):
        return json.loads(self.map) if self.map is not None else dict()

    def to_dict(self):
        response = dict(id=self.id,
                        type=self.type,
                        map=self.map_dict,
                        data=dict([(i.id, json.loads(i.data)) for i in self.item_data]),
                        links=dict([(i.type, i.linked_id) for i in self.item_links]))
        return response

    @classmethod
    def get(cls, item_id, **kwargs):
        return cls.query.filter_by(id=item_id, **kwargs).first()

    @classmethod
    def create(cls, type=None, map=None):
        item = cls(type=type, map=map)
        db.session.add(item)
        db.session.flush()
        return item
