from . import db
from geordi.data.model.item_data import ItemData
from geordi.data.model.item_link import ItemLink
import json


class Item(db.Model):
    __tablename__ = 'item'
    __table_args__ = {'schema': 'geordi'}

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Unicode)
    map = db.Column(db.UnicodeText)

    item_data = db.relationship('ItemData', cascade='delete', backref='item')
    item_redirects = db.relationship('ItemRedirect', cascade='delete', backref='new')

    # Item links
    item_links = db.relationship('ItemLink', cascade='delete', backref='item', foreign_keys='ItemLink.item_id')
    items_linked = db.relationship('ItemLink', cascade='delete', backref='linked', foreign_keys='ItemLink.linked_id')

    # Matches
    raw_matches = db.relationship('RawMatch', cascade='delete', backref='item')

    def delete(self):
        db.session.delete(self)
        return self

    @classmethod
    def get(cls, item_id, **kwargs):
        return cls.query.filter_by(id=item_id, **kwargs).first()

    @classmethod
    def create(cls, type=None, map=None):
        item = cls(type=type, map=map)
        db.session.add(item)
        return item

    @classmethod
    def update_map(cls, item_map, item_id):
        item = cls.get(item_id)
        item.map = item_map

    @classmethod
    def get_item_data(cls, item_id):
        """Fetch and return an item's data."""
        ret = {'id': item_id, 'data': [], 'map': {}, 'type': ''}

        result = ItemData.get_by_item_id(item_id)
        if len(result) > 0:
            data = dict([(d.id, json.loads(d.data)) for d in result])
            ret['data'] = data
        else:
            return None

        item = cls.get(item_id)
        if item is not None:
            if item.map is not None:
                ret['map'] = json.loads(item.map)
            if item.type is not None:
                ret['type'] = item.type

        # XXX: backwards links
        result = ItemLink.get_by_item_id(item_id)
        if len(result) > 0:
            links = dict([(d.type, d.linked_id) for d in result])
            ret['links'] = links

        return ret
