from geordi.test_case import GeordiTestCase
from geordi.data.model.item import Item
from geordi.data.model.editor import Editor
from . import db


class ItemTestCase(GeordiTestCase):

    def test_delete(self):
        items = Item.query.all()
        assert len(items) == 0

        item = Item()
        db.session.add(item)
        db.session.flush()

        items = Item.query.all()
        assert len(items) == 1

        item.delete()

        items = Item.query.all()
        assert len(items) == 0

    def test_get(self):
        item = Item()
        db.session.add(item)
        db.session.flush()

        same_item = Item.get(item.id)
        assert item == same_item

        missing_item = Editor.get('Unknown')
        assert missing_item is None

    def test_create(self):
        items = Item.query.all()
        assert len(items) == 0

        item_1 = Item.create('Type A')

        items = Item.query.all()
        assert len(items) == 1
        assert items[0] == item_1

        item_2 = Item.create('Type B')

        items = Item.query.all()
        assert len(items) == 2
        assert item_1 in items and item_2 in items
        assert item_1 != item_2
