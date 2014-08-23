from geordi.test_case import GeordiTestCase
from geordi.data.model.raw_match_entity import RawMatchEntity
from geordi.data.model.raw_match import RawMatch
from geordi.data.model.entity import Entity
from geordi.data.model.item import Item
from geordi.data.model.editor import Editor
from . import db
from datetime import datetime


class RawMatchEntityTestCase(GeordiTestCase):

    def setUp(self):
        super(RawMatchEntityTestCase, self).setUp()

        # Helper items
        self.editor = Editor(name='Tester')
        db.session.add(self.editor)
        self.item = Item()
        db.session.add(self.item)
        db.session.flush()
        self.match = RawMatch(item_id=self.item.id, editor_name=self.editor.name, timestamp=datetime.now())
        db.session.add(self.match)
        self.entity = Entity(mbid='f27ec8db-af05-4f36-916e-3d57f91ecf5e', type='test')
        db.session.add(self.entity)
        db.session.flush()

    def test_delete(self):
        self.assertEqual(RawMatchEntity.query.count(), 0)

        match_entity = RawMatchEntity(raw_match_id=self.match.id, entity_mbid=self.entity.mbid)
        db.session.add(match_entity)
        db.session.flush()
        self.assertEqual(RawMatchEntity.query.count(), 1)

        match_entity.delete()
        self.assertEqual(RawMatchEntity.query.count(), 0)
