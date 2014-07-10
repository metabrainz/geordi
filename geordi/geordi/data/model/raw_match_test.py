from geordi.test_case import GeordiTestCase
from geordi.data.model.raw_match import RawMatch
from geordi.data.model.item import Item
from geordi.data.model.editor import Editor
from . import db
from datetime import datetime


class RawMatchTestCase(GeordiTestCase):

    def test_delete(self):
        matches = RawMatch.query.all()
        assert len(matches) == 0

        # Helper items
        editor = Editor(name='Tester')
        db.session.add(editor)
        item = Item()
        db.session.add(item)
        db.session.flush()

        match = RawMatch(item_id=item.id, editor_name=editor.name, timestamp=datetime.now())
        db.session.add(match)
        db.session.flush()

        matches = RawMatch.query.all()
        assert len(matches) == 1
        assert matches[0] == match

        match.delete()

        entities = RawMatch.query.all()
        assert len(entities) == 0
