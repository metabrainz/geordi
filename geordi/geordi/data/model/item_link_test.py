from geordi.test_case import GeordiTestCase
from geordi.data.model.item_link import ItemLink
from geordi.data.model.item import Item


class ItemLinkTestCase(GeordiTestCase):

    def test_find_or_insert(self):
        items = ItemLink.query.all()
        assert len(items) == 0

        link_type = 'test'
        test_item_1 = Item.create()
        test_item_2 = Item.create()

        link_1 = ItemLink.find_or_insert(test_item_1.id, test_item_2.id, link_type)

        items = ItemLink.query.all()
        assert len(items) == 1
        assert items[0] == link_1

        link_2 = ItemLink.find_or_insert(test_item_1.id, test_item_2.id, link_type)

        items = ItemLink.query.all()
        assert len(items) == 1
        assert items[0] == link_2
        assert link_1 == link_2

