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