from flask.ext.login import UserMixin

class User(UserMixin):
    def __init__(self, id, tz=None):
        self.id = id
        self.tz = tz
