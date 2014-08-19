from geordi.test_case import GeordiTestCase
from geordi.data.model.item_data import ItemData
from geordi.data.model.item import Item
from . import db


class ItemDataTestCase(GeordiTestCase):

    def test_get(self):
        item = Item()
        db.session.add(item)
        db.session.flush()

        id = 'item-data-1'
        item_data = ItemData(id=id, item_id=item.id)
        db.session.add(item_data)
        db.session.flush()

        same_item_data = ItemData.get(id)
        self.assertEqual(item_data, same_item_data)

        missing_item_data = ItemData.get('unknown')
        self.assertIsNone(missing_item_data)

    def test_delete(self):
        # Helper item
        item = Item()
        db.session.add(item)
        db.session.flush()

        self.assertEqual(ItemData.query.count(), 0)

        item_data = ItemData(id='item-data-1', item_id=item.id)
        db.session.add(item_data)
        db.session.flush()
        self.assertEqual(ItemData.query.count(), 1)

        item_data.delete()
        self.assertEqual(ItemData.query.count(), 0)
