"""
geordi.data.model.raw_match
---------------------------
"""
from . import db
from .mixins import DeleteMixin


class RawMatch(db.Model, DeleteMixin):
    """Model for the 'raw_match' table, storing matches between items and MusicBrainz entities."""
    __tablename__ = 'raw_match'
    __table_args__ = {'schema': 'geordi'}

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
    raw_match_entities = db.relationship('RawMatchEntity', cascade='delete', backref='raw_match')
