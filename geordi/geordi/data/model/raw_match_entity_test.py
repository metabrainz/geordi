from geordi.test_case import GeordiTestCase
from geordi.data.model.raw_match_entity import RawMatchEntity
from geordi.data.model.raw_match import RawMatch
from geordi.data.model.entity import Entity
from geordi.data.model.item import Item
from geordi.data.model.editor import Editor
from . import db
from datetime import datetime


class RawMatchEntityTestCase(GeordiTestCase):

    def test_delete(self):
        self.assertEqual(RawMatchEntity.query.count(), 0)

        # Helper items
        editor = Editor(name='Tester')
        db.session.add(editor)
        item = Item()
        db.session.add(item)
        db.session.flush()
        match = RawMatch(item_id=item.id, editor_name=editor.name, timestamp=datetime.now())
        db.session.add(match)
        entity = Entity(mbid='f27ec8db-af05-4f36-916e-3d57f91ecf5e', type='test')
        db.session.add(entity)
        db.session.flush()

        match_entity = RawMatchEntity(raw_match_id=match.id, entity_mbid=entity.mbid)
        db.session.add(match_entity)
        db.session.flush()

        match_entities = RawMatchEntity.query.all()
        self.assertEqual(len(match_entities), 1)
        self.assertEqual(match_entities[0], match_entity)

        match.delete()
        self.assertEqual(RawMatchEntity.query.count(), 0)
