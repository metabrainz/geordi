"""
geordi.data.model.raw_match_entity
----------------------------------
"""
from . import db
from .mixins import DeleteMixin
from sqlalchemy.dialects.postgresql import UUID


class RawMatchEntity(db.Model, DeleteMixin):
    """Model for the 'raw_match_entity' table, storing the link between matches and materialized entity data."""
    __tablename__ = 'raw_match_entity'
    __table_args__ = {'schema': 'geordi'}

    #: The ID of the match.
    raw_match_id = db.Column('raw_match', db.Integer, db.ForeignKey('geordi.raw_match.id', ondelete='CASCADE'), primary_key=True)
    #: The MBID of the entity.
    entity_mbid = db.Column('entity', UUID, db.ForeignKey('geordi.entity.mbid', ondelete='CASCADE'), primary_key=True)
