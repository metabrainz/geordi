from . import db


class Editor(db.Model):
    __tablename__ = 'editor'
    __table_args__ = {'schema': 'geordi'}

    name = db.Column(db.Text, primary_key=True)
    tz = db.Column(db.Text)
    internal = db.Column(db.Boolean, nullable=False, default=False)

    matches = db.relationship('RawMatch', cascade='delete', backref='editor')

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self