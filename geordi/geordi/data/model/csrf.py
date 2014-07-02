from . import db
import json


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

    @staticmethod
    def update_csrf(ip, rand):
        db.session.execute("DELETE FROM csrf WHERE ip = :ip AND timestamp < NOW() - INTERVAL '1 hour'", {'ip': ip})
        db.session.execute("INSERT INTO csrf (ip, csrf, timestamp) VALUES (:ip, :rand, now())",
                           {'ip': ip, 'rand': rand})
        db.session.commit()

    @staticmethod
    def get_opts(csrf, ip):
        return db.session.execute('SELECT opts FROM csrf WHERE csrf = :csrf AND ip = :ip', {'csrf': csrf, 'ip': ip})

    @staticmethod
    def update_opts(opts, csrf):
        print json.dumps(opts)
        db.session.execute('UPDATE csrf SET opts = :opts WHERE csrf = :csrf', {'opts': json.dumps(opts), 'csrf': csrf})
        db.session.commit()

    @staticmethod
    def delete_csrf(csrf):
        db.session.execute('DELETE FROM csrf WHERE csrf = :csrf', {'csrf': csrf})
        db.session.commit()
