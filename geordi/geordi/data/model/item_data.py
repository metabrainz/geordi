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