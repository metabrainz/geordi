from . import db


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