from . import db
from sqlalchemy.dialects.postgresql import UUID


class RawMatchEntity(db.Model):
    __tablename__ = 'raw_match_entity'
    __table_args__ = {'schema': 'geordi'}

    raw_match_id = db.Column('raw_match', db.Integer, db.ForeignKey('geordi.raw_match.id', ondelete='CASCADE'), primary_key=True)
    entity_mbid = db.Column('entity', UUID, db.ForeignKey('geordi.entity.mbid', ondelete='CASCADE'), primary_key=True)

    def delete(self):
        db.session.delete(self)
        return self
