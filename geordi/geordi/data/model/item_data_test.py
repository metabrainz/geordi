from geordi.test_case import GeordiTestCase
from geordi.data.model.item_data import ItemData
from geordi.data.model.item import Item
from . import db


class ItemDataTestCase(GeordiTestCase):

    def setUp(self):
        super(ItemDataTestCase, self).setUp()

        # Item that will be used to create ItemData instances.
        self.item = Item()
        db.session.add(self.item)
        db.session.flush()

    def test_get(self):
        id = 'test/artist/Tester'
        item_data = ItemData(id=id, item_id=self.item.id)
        db.session.add(item_data)
        db.session.flush()

        same_item_data = ItemData.get(id)
        self.assertEqual(item_data, same_item_data)

        missing_item_data = ItemData.get('unknown')
        self.assertIsNone(missing_item_data)

    def test_get_by_item_id(self):
        item_data = ItemData(id='test/artist/Tester', item_id=self.item.id)
        db.session.add(item_data)
        db.session.flush()

        results = ItemData.get_by_item_id(self.item.id)
        self.assertListEqual(results, [item_data])

        missing_results = ItemData.get_by_item_id(self.item.id + 1)
        self.assertListEqual(missing_results, [])

    def test_update(self):
        item_data = ItemData(id='test/artist/Tester', item_id=self.item.id)
        db.session.add(item_data)
        db.session.flush()

        another_item = Item()
        db.session.add(another_item)
        db.session.flush()

        updated_item_data = ItemData.update(data_id=item_data.id, item_id=another_item.id, data='{"data": true}')

        self.assertEqual(item_data, updated_item_data)

    def test_to_dict(self):
        item_data = ItemData(id='test/artist/Tester', item_id=self.item.id)
        db.session.add(item_data)
        db.session.flush()
        self.assertDictEqual(item_data.to_dict(),
                             {'id': item_data.id, 'item_id': item_data.item_id, 'data': item_data.data})

        # Let's add some data
        item_data.data = '{"data": true}'
        db.session.flush()
        self.assertDictEqual(item_data.to_dict(),
                             {'id': item_data.id, 'item_id': item_data.item_id, 'data': '{"data": true}'})

    def test_delete(self):
        self.assertEqual(ItemData.query.count(), 0)

        item_data = ItemData(id='test/artist/Tester', item_id=self.item.id)
        db.session.add(item_data)
        db.session.flush()
        self.assertEqual(ItemData.query.count(), 1)

        item_data.delete()
        self.assertEqual(ItemData.query.count(), 0)
