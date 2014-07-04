from . import db


class RawMatch(db.Model):
    __tablename__ = 'raw_match'
    __table_args__ = {'schema': 'geordi'}

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column('item', db.Integer, db.ForeignKey('geordi.item.id', ondelete='CASCADE'), nullable=False)
    editor_name = db.Column('editor', db.Text, db.ForeignKey('geordi.editor.name', ondelete='CASCADE'), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False)
    superseded = db.Column(db.Boolean, nullable=False, default=False)

    raw_match_entities = db.relationship('RawMatchEntity', cascade='delete', backref='raw_match')

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self
