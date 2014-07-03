from . import db


class ItemLink(db.Model):
    __tablename__ = 'item_link'
    __table_args__ = {'schema': 'geordi'}

    type = db.Column(db.Text, nullable=False, primary_key=True)
    item_id = db.Column('item', db.Integer, db.ForeignKey('geordi.item.id', ondelete='CASCADE'), primary_key=True)
    linked_id = db.Column('linked', db.Integer, db.ForeignKey('geordi.item.id', ondelete='CASCADE'), primary_key=True)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @staticmethod
    def upsert(node_item, target_item, link_type):
        result = db.session.execute('SELECT TRUE FROM item_link '
                                    'WHERE item = :item AND linked = :linked AND type = :type',
                                    {'item': node_item, 'linked': target_item, 'type': link_type})
        if result.rowcount == 0:
            db.session.execute('INSERT INTO item_link (item, linked, type) VALUES (:item, :linked, :type)',
                               {'item': node_item, 'linked': target_item, 'type': link_type})
            db.session.commit()
