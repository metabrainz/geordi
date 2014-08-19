from geordi.test_case import GeordiTestCase
from geordi.data.model.item_link import ItemLink
from geordi.data.model.item import Item
from . import db


class ItemLinkTestCase(GeordiTestCase):

    def setUp(self):
        super(ItemLinkTestCase, self).setUp()

        self.link_type = 'test'
        self.item_1 = Item.create()
        self.item_2 = Item.create()

    def test_find_or_insert(self):
        self.assertEqual(ItemLink.query.count(), 0)

        link_1 = ItemLink.find_or_insert(self.item_1.id, self.item_2.id, self.link_type)

        links = ItemLink.query.all()
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0], link_1)

        link_2 = ItemLink.find_or_insert(self.item_1.id, self.item_2.id, self.link_type)

        links = ItemLink.query.all()
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0], link_2)
        self.assertEqual(link_1, link_2)

    def test_delete_by_item_id(self):
        self.assertEqual(ItemLink.query.count(), 0)

        linked_item = Item.create()

        link_1 = ItemLink(type=self.link_type, item_id=self.item_1.id, linked_id=linked_item.id)
        link_2 = ItemLink(type=self.link_type, item_id=self.item_2.id, linked_id=linked_item.id)
        db.session.add(link_1)
        db.session.add(link_2)
        db.session.flush()

        links = ItemLink.query.all()
        self.assertEqual(len(links), 2)
        self.assertIn(link_1, links)
        self.assertIn(link_2, links)

        ItemLink.delete_by_item_id(self.item_1.id)

        links = ItemLink.query.all()
        self.assertEqual(len(links), 1)
        self.assertNotIn(link_1, links)
        self.assertIn(link_2, links)

        ItemLink.delete_by_item_id(self.item_2.id)

        self.assertEqual(ItemLink.query.count(), 0)

    def test_to_dict(self):
        item_link = ItemLink(type=self.link_type, item_id=self.item_1.id, linked_id=self.item_2.id)
        db.session.add(item_link)
        db.session.flush()
        self.assertDictEqual(item_link.to_dict(),
                             {'type': item_link.type, 'item_id': item_link.item_id, 'linked_id': item_link.linked_id})

    def test_get_by_item_id(self):
        item_link = ItemLink(type=self.link_type, item_id=self.item_1.id, linked_id=self.item_2.id)
        db.session.add(item_link)
        db.session.flush()

        results = ItemLink.get_by_item_id(self.item_1.id)
        self.assertListEqual(results, [item_link])

        missing_results = ItemLink.get_by_item_id(self.item_2.id)
        self.assertListEqual(missing_results, [])
