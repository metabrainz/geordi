from . import db


class ItemData(db.Model):
    __tablename__ = 'item_data'
    __table_args__ = {'schema': 'geordi'}

    id = db.Column(db.Text, primary_key=True)
    item_id = db.Column('item', db.Integer, db.ForeignKey('geordi.item.id', ondelete='CASCADE'), nullable=False)
    data = db.Column(db.Text)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @staticmethod
    def get_indexes():
        result = db.session.execute("SELECT DISTINCT regexp_replace(id, '/.*$', '') FROM item_data")
        return [i[0] for i in result]

    @staticmethod
    def get_item_types_by_index(index):
        result = db.session.execute("SELECT DISTINCT regexp_replace(id, '^[^/]*/([^/]*)/.*$', '\\1') "
                                    "FROM item_data "
                                    "WHERE id ~ ('^' || :index || '/')",
                                    {'index': index})
        return [i[0] for i in result.fetchall()]

    @staticmethod
    def get_item_ids(index, item_type):
        result = db.session.execute("SELECT DISTINCT regexp_replace(id, '^[^/]*/[^/]*/(.*)$', '\\1') "
                                    "FROM item_data "
                                    "WHERE id ~ ('^' || :index || '/' || :item_type || '/')",
                                    {'index': index, 'item_type': item_type})
        return [i[0] for i in result.fetchall()]

    @staticmethod
    def data_to_item(data_id):
        """Resolve a data ID to its associated item ID, if it has one (it should!)"""
        item_id = None
        result = db.session.execute("SELECT item FROM item_data WHERE id = :id", {'id': data_id})
        if result.rowcount == 1:
            (item_id,) = result.fetchone()
        elif result.rowcount > 1:
            raise Exception("More than one item found, that can't be right")
        return item_id

    @staticmethod
    def delete_data_item(data_id):
        result = db.session.execute("DELETE FROM item_data WHERE id = :id RETURNING item", {'id': data_id})
        item = result.fetchone()[0]
        db.session.execute("DELETE FROM item_link "
                           "WHERE (item = :item OR linked = :item) "
                           "AND (NOT EXISTS (SELECT TRUE FROM item_data WHERE item = item_link.item) "
                           "OR NOT EXISTS (SELECT TRUE FROM item_data WHERE item = item_link.linked))",
                           {'item': item})
        db.session.execute("DELETE FROM item "
                           "WHERE id = :item AND NOT EXISTS (SELECT TRUE FROM item_data WHERE item = item.id)",
                           {'item': item})
