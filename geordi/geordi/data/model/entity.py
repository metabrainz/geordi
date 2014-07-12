"""
geordi.data.model.entity
------------------------
"""
from . import db
from .mixins import DeleteMixin
from sqlalchemy.dialects.postgresql import UUID


class Entity(db.Model, DeleteMixin):
    """Model for the 'entity' table, storing materialized information about entities in MusicBrainz."""
    __tablename__ = 'entity'
    __table_args__ = {'schema': 'geordi'}

    #: The entity's MBID.
    mbid = db.Column(UUID, primary_key=True)
    #: The type of entity (e.g. 'release', 'release_group', 'artist', etc.
    type = db.Column(db.Unicode, nullable=False)
    #: Materialized JSON data used to display a link (e.g. the name or title).
    data = db.Column(db.UnicodeText)

    #: Property for matches using this entity.
    raw_match_entities = db.relationship('RawMatchEntity', cascade='delete', backref='entity')
