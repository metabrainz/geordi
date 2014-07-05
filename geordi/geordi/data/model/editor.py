from . import db


class Editor(db.Model):
    __tablename__ = 'editor'
    __table_args__ = {'schema': 'geordi'}

    name = db.Column(db.Unicode, primary_key=True)
    tz = db.Column(db.Unicode)
    internal = db.Column(db.Boolean, nullable=False, default=False)

    matches = db.relationship('RawMatch', cascade='delete', backref='editor')

    @classmethod
    def get(cls, name, **kwargs):
        return cls.query.filter_by(name=name, **kwargs).first()

    @classmethod
    def add_or_update(cls, name, tz):
        editor = cls.query.filter_by(name=name).first()
        if editor is None:
            editor = cls(name=name)
            db.session.add(editor)
        editor.tz = tz
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self
