"""
geordi.data.model.item_link
---------------------------
"""
from . import db
from .mixins import DeleteMixin
from geordi.data.mapping.extract import extract_value
import re


class ItemLink(db.Model, DeleteMixin):
    """Model for the 'item_link' table, storing automatically-extracted links between items."""
    __tablename__ = 'item_link'
    __table_args__ = {'schema': 'geordi'}

    #: Type of this link, expressed as a path into the mapped JSON data of the source item, joined by '%' characters.
    type = db.Column(db.Unicode, nullable=False, primary_key=True)
    #: Item ID of the source side of this link.
    item_id = db.Column('item', db.Integer, db.ForeignKey('geordi.item.id', ondelete='CASCADE'), primary_key=True)
    #: Item ID of the target side of this link.
    linked_id = db.Column('linked', db.Integer, db.ForeignKey('geordi.item.id', ondelete='CASCADE'), primary_key=True)

    @property
    def value(self):
        path = [(int(x) if re.match('^\d+$', x) else x) for x in self.type.split('%')]
        return extract_value(self.item.map_dict, path)[0][1]

    def to_dict(self):
        return {'type': self.type, 'item_id': self.item_id, 'linked_id': self.linked_id}

    @classmethod
    def get(cls, type, item_id, linked_id, **kwargs):
        return cls.query.filter_by(type=type, item_id=item_id, linked_id=linked_id, **kwargs).first()

    @classmethod
    def get_by_item_id(cls, item_id, **kwargs):
        return cls.query.filter_by(item_id=item_id, **kwargs).all()

    @classmethod
    def find_or_insert(cls, node_item_id, target_item_id, link_type):
        link = cls.get(type=link_type, item_id=node_item_id, linked_id=target_item_id)
        if link is None:
            link = cls(type=link_type, item_id=node_item_id, linked_id=target_item_id)
            db.session.add(link)
            db.session.flush()
        return link

    @classmethod
    def delete_by_item_id(cls, item_id, **kwargs):
        cls.query.filter_by(item_id=item_id, **kwargs).delete()
        db.session.flush()
