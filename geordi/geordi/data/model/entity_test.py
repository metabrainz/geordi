from geordi.test_case import GeordiTestCase
from geordi.data.model.entity import Entity
from . import db


class EntityTestCase(GeordiTestCase):

    def test_delete(self):
        self.assertEqual(Entity.query.count(), 0)

        entity = Entity(mbid='f27ec8db-af05-4f36-916e-3d57f91ecf5e', type='test')
        db.session.add(entity)
        db.session.flush()

        entities = Entity.query.all()
        self.assertEqual(len(entities), 1)
        self.assertEqual(entities[0], entity)

        entity.delete()
        self.assertEqual(Entity.query.count(), 0)
