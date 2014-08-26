"""
geordi.data.model.csrf
----------------------
"""
from . import db
from .mixins import DeleteMixin
from datetime import datetime, timedelta


class CSRF(db.Model, DeleteMixin):
    """Model for the 'csrf' table, storing information about users who may be
    logging in via MusicBrainz OAuth."""
    __tablename__ = 'csrf'
    __table_args__ = {'schema': 'geordi'}

    #: The user's IP, after stripping away known/trusted proxies.
    ip = db.Column(db.Unicode, nullable=False)
    #: The random csrf value passed as the 'state' to MusicBrainz's OAuth.
    csrf = db.Column(db.Unicode, nullable=False, primary_key=True)
    #: JSON representation of user options, e.g. 'remember me' and the URL to return to.
    opts = db.Column(db.UnicodeText)
    #: Timestamp for when this was allocated, used for automatic removal.
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    @classmethod
    def get(cls, csrf, **kwargs):
        return cls.query.filter_by(csrf=csrf, **kwargs).first()

    @classmethod
    def update_csrf(cls, ip, rand):
        """Called with an ip and a random value to be used as a csrf. Inserts
        this into the DB and automatically deletes other values for this IP
        older than 1 hour."""
        db.session.query(cls).\
            filter(cls.ip == ip).\
            filter(cls.timestamp < datetime.today() - timedelta(hours=1)).\
            delete()
        db.session.add(cls(ip=ip, csrf=rand))
        db.session.flush()
