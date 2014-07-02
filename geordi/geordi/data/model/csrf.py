from . import db


class CSRF(db.Model):
    __tablename__ = 'csrf'
    __table_args__ = {'schema': 'geordi'}

    ip = db.Column(db.Text, nullable=False)
    csrf = db.Column(db.Text, nullable=False, primary_key=True)
    opts = db.Column(db.Text)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=False)

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self