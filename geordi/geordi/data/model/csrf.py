from . import db
import json
from datetime import datetime, timedelta


class CSRF(db.Model):
    __tablename__ = 'csrf'
    __table_args__ = {'schema': 'geordi'}

    ip = db.Column(db.Text, nullable=False)
    csrf = db.Column(db.Text, nullable=False, primary_key=True)
    opts = db.Column(db.Text)
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
        old_csrf = db.session.query(cls).\
            filter(cls.ip == ip).\
            filter(cls.timestamp < datetime.today() - timedelta(hours=1)).all()
        for csrf in old_csrf:
            csrf.delete()
        db.session.add(cls(ip=ip, csrf=rand))
        db.session.commit()

    @classmethod
    def update_opts(cls, opts, csrf):
        csrf = cls.get(csrf)
        csrf.opts = json.dumps(opts)
        db.session.commit()
