"""
geordi.data.model.editor
------------------------
"""
from . import db
from .mixins import DeleteMixin


class Editor(db.Model, DeleteMixin):
    """Model for the 'editor' table, storing information about both human users
    and automated processes which match items."""
    __tablename__ = 'editor'
    __table_args__ = {'schema': 'geordi'}

    #: Editor name from MusicBrainz, or a descriptive name for an automated process.
    name = db.Column(db.Unicode, primary_key=True)
    #: For human editors, timezone preference.
    tz = db.Column(db.Unicode)
    #: Boolean; True for automated processes, otherwise False.
    internal = db.Column(db.Boolean, nullable=False, default=False)

    #: Property for matches entered by this user. Not loaded by default.
    matches = db.relationship('RawMatch', cascade='delete', backref=db.backref('editor', lazy='joined'))

    @classmethod
    def get(cls, name, **kwargs):
        return cls.query.filter_by(name=name, **kwargs).first()

    @classmethod
    def add_or_update(cls, name, tz=None):
        """Given a name and optionally a timezone, either insert a new row,
        update the timezone preference, or do nothing, depending on what's
        already stored."""
        editor = cls.query.filter_by(name=name).first()
        if editor is None:
            editor = cls(name=name)
            db.session.add(editor)
        editor.tz = tz
        db.session.flush()
        return editor
