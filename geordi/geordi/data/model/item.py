from . import db
import json


class Item(db.Model):
    __tablename__ = 'item'
    __table_args__ = {'schema': 'geordi'}

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Unicode)
    map = db.Column(db.UnicodeText)

    item_data = db.relationship('ItemData', lazy='joined', cascade='delete', backref='item')
    item_redirects = db.relationship('ItemRedirect', cascade='delete', backref='new')

    # Item links
    item_links = db.relationship('ItemLink', lazy='joined', cascade='delete', backref='item', foreign_keys='ItemLink.item_id')
    items_linked = db.relationship('ItemLink', cascade='delete', backref='linked', foreign_keys='ItemLink.linked_id')

    # Matches
    raw_matches = db.relationship('RawMatch', cascade='delete', backref='item')

    def to_dict(self):
        response = dict(id=self.id,
                        type=self.type,
                        map=json.loads(self.map) if self.map is not None else None,
                        data=dict([(i.id, json.loads(i.data)) for i in self.item_data]),
                        links=dict([(i.type, i.linked_id) for i in self.item_links]))
        return response

    def delete(self):
        db.session.delete(self)
        db.session.flush()
        return self

    @classmethod
    def get(cls, item_id, **kwargs):
        return cls.query.filter_by(id=item_id, **kwargs).first()

    @classmethod
    def create(cls, type=None, map=None):
        item = cls(type=type, map=map)
        db.session.add(item)
        db.session.flush()
        return item
