from geordi.test_case import GeordiTestCase
from geordi.data.model.raw_match import RawMatch
from geordi.data.model.entity import Entity
from geordi.data.model.item import Item
from geordi.data.model.editor import Editor
from . import db
from datetime import datetime


class RawMatchTestCase(GeordiTestCase):
    def setUp(self):
        super(RawMatchTestCase, self).setUp()

        # Helper items

        self.editor = Editor(name='Tester')
        db.session.add(self.editor)

        self.item = Item()
        db.session.add(self.item)
        db.session.flush()

        self.entity_1 = Entity(mbid='f27ec8db-af05-4f36-916e-3d57f91ecf5e', type='test')
        self.entity_2 = Entity(mbid='85d9c621-e30f-4788-a962-a089c0d34182', type='another')
        db.session.add(self.entity_1)
        db.session.add(self.entity_2)
        db.session.flush()

    def test_match_item(self):
        match = RawMatch.match_item(item_id=self.item.id, editor_name=self.editor.name,
                                    entities=[self.entity_1, self.entity_2])
        self.assertEqual(match.item.id, self.item.id)
        self.assertEqual(match.editor, self.editor)
        # TODO: Check entities

    def test_to_dict(self):
        match = RawMatch(item_id=self.item.id, editor_name=self.editor.name, timestamp=datetime.now())
        db.session.add(match)
        self.assertDictEqual(match.to_dict(),
                             {
                                 'id': match.id,
                                 'item': match.item_id,
                                 'timestamp': match.timestamp,
                                 'superseded': match.superseded,
                                 'entities': [e.entity.to_dict() for e in match.entities],
                             })

