"""
geordi.data.model.item_data
---------------------------
"""
from . import db
from .mixins import DeleteMixin


class ItemData(db.Model, DeleteMixin):
    """Model for the 'item_data' table, storing index-specific raw data."""
    __tablename__ = 'item_data'
    __table_args__ = {'schema': 'geordi'}

    #: Data item identifier of the form (index)/(item type)/(identifier).
    id = db.Column(db.Unicode, primary_key=True)
    #: Item ID of the item to which this data item belongs.
    item_id = db.Column('item', db.Integer, db.ForeignKey('geordi.item.id', ondelete='CASCADE'), nullable=False)
    #: Raw JSON data.
    data = db.Column(db.UnicodeText)

    def to_dict(self):
        return {'id': self.id, 'item_id': self.item_id, 'data': self.data}

    @classmethod
    def get(cls, id, **kwargs):
        return cls.query.filter_by(id=id, **kwargs).first()

    @classmethod
    def get_by_item_id(cls, item_id, **kwargs):
        return cls.query.filter_by(item_id=item_id, **kwargs).all()

    @classmethod
    def data_to_item(cls, data_id):
        """Resolve a data ID to its associated item ID, if it has one (it should)."""
        item_data = cls.get(data_id)
        if item_data is not None:
            return item_data.item_id
        else:
            return None

    @classmethod
    def create(cls, item_id, data_json, data_id):
        item_data = cls(item_id=item_id, data=data_json, id=data_id)
        db.session.add(item_data)
        db.session.flush()
        return item_data

    @classmethod
    def update(cls, item_id, data, data_id):
        item_data = cls.get(data_id)
        item_data.item_id = item_id
        item_data.data = data
        db.session.flush()
        return item_data

    @staticmethod
    def get_indexes():
        result = db.session.execute("SELECT DISTINCT regexp_replace(id, '/.*$', '') n FROM geordi.item_data ORDER BY n")
        return [i[0] for i in result]

    @staticmethod
    def get_item_types_by_index(index):
        result = db.session.execute("SELECT DISTINCT regexp_replace(id, '^[^/]*/([^/]*)/.*$', '\\1') n "
                                    "FROM geordi.item_data "
                                    "WHERE id ~ ('^' || :index || '/') "
                                    "ORDER BY n",
                                    {'index': index})
        return [i[0] for i in result.fetchall()]

    @staticmethod
    def get_item_ids(index, item_type):
        result = db.session.execute("SELECT DISTINCT regexp_replace(id, '^[^/]*/[^/]*/(.*)$', '\\1') n "
                                    "FROM geordi.item_data "
                                    "WHERE id ~ ('^' || :index || '/' || :item_type || '/') "
                                    "ORDER BY n",
                                    {'index': index, 'item_type': item_type})
        return [i[0] for i in result.fetchall()]

    @staticmethod
    def delete_data_item(data_id):
        result = db.session.execute("DELETE FROM geordi.item_data WHERE id = :id RETURNING item", {'id': data_id})
        item = result.fetchone()[0]
        db.session.execute("DELETE FROM geordi.item_link "
                           "WHERE (item = :item OR linked = :item) "
                           "  AND (NOT EXISTS (SELECT TRUE FROM item_data WHERE item = item_link.item) "
                           "  OR NOT EXISTS (SELECT TRUE FROM item_data WHERE item = item_link.linked))",
                           {'item': item})
        db.session.execute("DELETE FROM item "
                           "WHERE id = :item AND NOT EXISTS (SELECT TRUE FROM geordi.item_data WHERE item = item.id)",
                           {'item': item})
        db.session.flush()
