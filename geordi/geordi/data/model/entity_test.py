from geordi.test_case import GeordiTestCase
from geordi.data.model.entity import Entity
from . import db


class EntityTestCase(GeordiTestCase):

    def test_get(self):
        entity = Entity(mbid='f27ec8db-af05-4f36-916e-3d57f91ecf5e', type='test')
        db.session.add(entity)
        db.session.flush()

        same_csrf = CSRF.get('some_random_string')
        self.assertEqual(csrf, same_csrf)

        missing_csrf = CSRF.get('another_random_string')
        self.assertIsNone(missing_csrf)
