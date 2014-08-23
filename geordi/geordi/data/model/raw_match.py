"""
geordi.data.model.raw_match
---------------------------
"""
from . import db
from .mixins import DeleteMixin
from .raw_match_entity import RawMatchEntity


class RawMatch(db.Model, DeleteMixin):
    """Model for the 'raw_match' table, storing matches between items and MusicBrainz entities."""
    __tablename__ = 'raw_match'
    __table_args__ = (db.Index('raw_match_idx_uniq', 'item', unique=True, postgresql_where=db.text('NOT superseded')),
                      {'schema': 'geordi'})

    #: A unique ID for the match.
    id = db.Column(db.Integer, primary_key=True)
    #: The item ID for the item this match is for.
    item_id = db.Column('item', db.Integer, db.ForeignKey('geordi.item.id', ondelete='CASCADE'), nullable=False)
    #: The editor name for the editor who created this match.
    editor_name = db.Column('editor', db.Unicode, db.ForeignKey('geordi.editor.name', ondelete='CASCADE'), nullable=False)
    #: The time when the match was made.
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False)
    #: Boolean, false if this match is current, true if it should be considered historical only.
    superseded = db.Column(db.Boolean, nullable=False, default=False)

    #: Property for raw match entities linking this match to MusicBrainz entities.
    entities = db.relationship('RawMatchEntity', lazy='joined', cascade='delete', backref='raw_match')

    @classmethod
    def get_by_item(cls, item_id, **kwargs):
        return cls.query.filter_by(item_id=item_id, **kwargs).all()

    @classmethod
    def match_item(cls, item_id, editor_name, entities):
        cls.query.filter_by(item_id=item_id, superseded=False).update({"superseded": True})
        match = cls(item_id=item_id, editor_name=editor_name, timestamp=db.func.now())
        db.session.add(match)
        for entity in entities:
            rm = RawMatchEntity(raw_match=match, entity=entity)
            db.session.add(rm)
        db.session.flush()
        return match

    def to_dict(self):
        return {
            'id': self.id,
            'item': self.item_id,
            'timestamp': self.timestamp,
            'superseded': self.superseded,
            'entities': [e.entity.to_dict() for e in self.entities],
        }
