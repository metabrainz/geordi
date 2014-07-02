from . import db
import json


class Item(db.Model):
    __tablename__ = 'item'
    __table_args__ = {'schema': 'geordi'}

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Text)
    map = db.Column(db.Text)

    item_data = db.relationship('ItemData', cascade='delete', backref='item')
    item_redirects = db.relationship('ItemRedirect', cascade='delete', backref='new')

    # Item links
    item_links = db.relationship('ItemLink', cascade='delete', backref='item', foreign_keys='ItemLink.item_id')
    items_linked = db.relationship('ItemLink', cascade='delete', backref='linked', foreign_keys='ItemLink.linked_id')

    # Matches
    raw_matches = db.relationship('RawMatch', cascade='delete', backref='item')

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @staticmethod
    def get_item(item_id):
        """Fetch and return an item's data."""
        ret = {'id': item_id, 'data': [], 'map': {}, 'type': ''}

        result = db.session.execute('SELECT map, type FROM item WHERE id = :id;', {'id': item_id})
        if result.rowcount > 0:
            row = result.fetchone()
            if row[0] is not None:
                ret['map'] = json.loads(row[0])
            if row[1] is not None:
                ret['type'] = row[1]

        # Getting data
        result = db.session.execute('SELECT id, data FROM item_data WHERE item = :id;', {'id': item_id})
        if result.rowcount > 0:
            data = dict([(d[0], json.loads(d[1])) for d in result.fetchall()])
            ret['data'] = data
        else:
            return None

        # Getting links
        # XXX: backwards links
        result = db.session.execute('SELECT type, linked FROM item_link WHERE item = :id;', {'id': item_id})
        if result.rowcount > 0:
            links = dict([(d[0], d[1]) for d in result.fetchall()])
            ret['links'] = links

        return ret
