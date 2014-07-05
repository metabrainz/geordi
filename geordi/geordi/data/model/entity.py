from . import db
from sqlalchemy.dialects.postgresql import UUID


class Entity(db.Model):
    __tablename__ = 'entity'
    __table_args__ = {'schema': 'geordi'}

    mbid = db.Column(UUID, primary_key=True)
    type = db.Column(db.Unicode, nullable=False)
    data = db.Column(db.UnicodeText)

    raw_match_entities = db.relationship('RawMatchEntity', cascade='delete', backref='entity')

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self
