from . import db
import json
from datetime import datetime, timedelta


class CSRF(db.Model):
    __tablename__ = 'csrf'
    __table_args__ = {'schema': 'geordi'}

    ip = db.Column(db.Unicode, nullable=False)
    csrf = db.Column(db.Unicode, nullable=False, primary_key=True)
    opts = db.Column(db.UnicodeText)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    @classmethod
    def get(cls, csrf, **kwargs):
        return cls.query.filter_by(csrf=csrf, **kwargs).first()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @classmethod
    def update_csrf(cls, ip, rand):
        db.session.query(cls).\
            filter(cls.ip == ip).\
            filter(cls.timestamp < datetime.today() - timedelta(hours=1)).\
            delete()
        db.session.add(cls(ip=ip, csrf=rand))
        db.session.commit()

    @classmethod
    def update_opts(cls, opts, csrf):
        csrf = cls.get(csrf)
        csrf.opts = json.dumps(opts)
        db.session.commit()
