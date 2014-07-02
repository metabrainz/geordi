from . import db


class ItemRedirect(db.Model):
    __tablename__ = 'item_redirect'
    __table_args__ = {'schema': 'geordi'}

    old_id = db.Column('old', db.Integer, primary_key=True)
    new_id = db.Column('new', db.Integer, db.ForeignKey('geordi.item.id', ondelete='CASCADE'))

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self