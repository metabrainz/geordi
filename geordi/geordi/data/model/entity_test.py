from geordi.test_case import GeordiTestCase
from geordi.data.model.entity import Entity
from . import db


class EntityTestCase(GeordiTestCase):

    def test_get(self):
        mbid = 'f27ec8db-af05-4f36-916e-3d57f91ecf5e'
        entity = Entity(mbid=mbid, type='test')
        db.session.add(entity)
        db.session.flush()

        same_entity = Entity.get(mbid)
        self.assertEqual(entity, same_entity)

        missing_csrf = Entity.get('85d9c621-e30f-4788-a962-a089c0d34182')
        self.assertIsNone(missing_csrf)

    def test_to_dict(self):
        entity_1 = Entity(mbid='f27ec8db-af05-4f36-916e-3d57f91ecf5e', type='test')
        db.session.add(entity_1)
        db.session.flush()
        self.assertDictEqual(entity_1.to_dict(),
                             {'mbid': entity_1.mbid, 'type': entity_1.type, 'data': {}})

        # Trying with data
        entity_2 = Entity(mbid='85d9c621-e30f-4788-a962-a089c0d34182', type='another_test', data='{"test": true}')
        db.session.add(entity_2)
        db.session.flush()
        self.assertDictEqual(entity_2.to_dict(),
                             {'mbid': entity_2.mbid, 'type': entity_2.type, 'data': {'test': True}})

    def test_delete(self):
        self.assertEqual(Entity.query.count(), 0)

        entity = Entity(mbid='f27ec8db-af05-4f36-916e-3d57f91ecf5e', type='test')
        db.session.add(entity)
        db.session.flush()
        self.assertEqual(Entity.query.count(), 1)

        entity.delete()
        self.assertEqual(Entity.query.count(), 0)
