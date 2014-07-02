from . import db


class Entity(db.Model):
    __tablename__ = 'entity'
    __table_args__ = {'schema': 'geordi'}

    mbid = db.Column(db.Text, primary_key=True)
    type = db.Column(db.Text, nullable=False)
    data = db.Column(db.Text)

    raw_match_entities = db.relationship('RawMatchEntity', cascade='delete', backref='entity')

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self
