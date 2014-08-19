from geordi.test_case import GeordiTestCase
from geordi.data.model.item import Item
from geordi.data.model.editor import Editor
from . import db


class ItemTestCase(GeordiTestCase):

    def test_delete(self):
        self.assertEqual(Item.query.count(), 0)

        item = Item()
        db.session.add(item)
        db.session.flush()
        self.assertEqual(Item.query.count(), 1)

        item.delete()
        self.assertEqual(Item.query.count(), 0)

    def test_get(self):
        item = Item()
        db.session.add(item)
        db.session.flush()

        same_item = Item.get(item.id)
        self.assertEqual(item, same_item)

        missing_item = Editor.get('Unknown')
        self.assertIsNone(missing_item)

    def test_create(self):
        self.assertEqual(Item.query.count(), 0)

        item_1 = Item.create('Type A')

        items = Item.query.all()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0], item_1)

        item_2 = Item.create('Type B')

        items = Item.query.all()
        self.assertEqual(len(items), 2)
        self.assertIn(item_1, items)
        self.assertIn(item_2, items)
        self.assertNotEqual(item_1, item_2)
