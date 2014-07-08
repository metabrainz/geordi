from flask.ext.testing import TestCase
from geordi import create_app
from . import db


class GeordiTestCase(TestCase):

    def create_app(self):
        app = create_app('test.cfg')
        app.config['TESTING'] = True
        app.config['CSRF_ENABLED'] = False
        return app

    def setUp(self):
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
