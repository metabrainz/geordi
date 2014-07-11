from . import db
from .raw_match_entity import RawMatchEntity

class RawMatch(db.Model):
    __tablename__ = 'raw_match'
    __table_args__ = (db.Index('raw_match_idx_uniq', 'item', unique=True, postgresql_where=db.text('NOT superseded')),
                      {'schema': 'geordi'})

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column('item', db.Integer, db.ForeignKey('geordi.item.id', ondelete='CASCADE'), nullable=False)
    editor_name = db.Column('editor', db.Unicode, db.ForeignKey('geordi.editor.name', ondelete='CASCADE'), nullable=False)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False)
    superseded = db.Column(db.Boolean, nullable=False, default=False)

    entities = db.relationship('RawMatchEntity', lazy='joined', cascade='delete', backref='raw_match')

    @classmethod
    def get_by_item(cls, item_id, **kwargs):
        return cls.query.filter_by(item_id=item_id, **kwargs).all()

    @classmethod
    def match_item(cls, item_id, editor, entities):
        cls.query.filter_by(item_id=item_id, superseded=False).update({"superseded": True})
        match = cls(item_id=item_id, editor_name=editor, timestamp=db.func.now())
        db.session.add(match)
        for entity in entities:
            rm = RawMatchEntity(raw_match=match, entity=entity)
            db.session.add(rm)
        db.session.flush()
        return match

    def delete(self):
        db.session.delete(self)
        db.session.flush()
        return self

    def to_dict(self):
        response = dict(id=self.id,
                        item=self.item_id,
                        timestamp=self.timestamp,
                        superseded=self.superseded,
                        entities=[e.entity.to_dict() for e in self.entities]
                        )
        return response
