from geordi.test_case import GeordiTestCase
from geordi.data.model.item_link import ItemLink
from geordi.data.model.item import Item
from . import db


class ItemLinkTestCase(GeordiTestCase):

    def test_find_or_insert(self):
        links = ItemLink.query.all()
        assert len(links) == 0

        link_type = 'test'
        test_item_1 = Item.create()
        test_item_2 = Item.create()

        link_1 = ItemLink.find_or_insert(test_item_1.id, test_item_2.id, link_type)

        links = ItemLink.query.all()
        assert len(links) == 1
        assert links[0] == link_1

        link_2 = ItemLink.find_or_insert(test_item_1.id, test_item_2.id, link_type)

        links = ItemLink.query.all()
        assert len(links) == 1
        assert links[0] == link_2
        assert link_1 == link_2

    def test_delete_by_item_id(self):
        links = ItemLink.query.all()
        assert len(links) == 0

        link_type = 'test'
        item_1 = Item.create()
        item_2 = Item.create()
        linked_item = Item.create()

        link_1 = ItemLink(type=link_type, item_id=item_1.id, linked_id=linked_item.id)
        link_2 = ItemLink(type=link_type, item_id=item_2.id, linked_id=linked_item.id)
        db.session.add(link_1)
        db.session.add(link_2)
        db.session.flush()

        links = ItemLink.query.all()
        assert len(links) == 2
        assert link_1 in links and link_2 in links

        ItemLink.delete_by_item_id(item_1.id)

        links = ItemLink.query.all()
        assert len(links) == 1
        assert link_1 not in links and link_2 in links

        ItemLink.delete_by_item_id(item_2.id)

        links = ItemLink.query.all()
        assert len(links) == 0
