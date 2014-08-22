from geordi.test_case import GeordiTestCase
from geordi.data.model.item import Item
from geordi.data.model.item_data import ItemData


class FrontendViewsTestCase(GeordiTestCase):

    def test_homepage(self):
        response = self.client.get("/")
        self.assert200(response)

    def test_item(self):
        item = Item.create()

        response = self.client.get("/item/%s" % item.id)
        self.assert200(response)
        response = self.client.get("/item/0%s" % item.id)
        self.assert200(response)

        response = self.client.get("/item/%s0" % item.id)
        self.assert404(response)
        response = self.client.get("/item/missing")
        self.assert404(response)

    def test_item_links(self):
        item = Item.create()

        response = self.client.get("/item/%s/links" % item.id)
        self.assert200(response)
        response = self.client.get("/item/0%s/links" % item.id)
        self.assert200(response)

        response = self.client.get("/item/%s0/links" % item.id)
        self.assert404(response)
        response = self.client.get("/item/missing/links")
        self.assert404(response)

    def test_list_indexes(self):
        response = self.client.get("/data")
        self.assert200(response)

    def test_list_index(self):
        item = Item.create()
        index = 'test'
        item_data = ItemData.create(item_id=item.id, data_json='{}', data_id='%s/album/lalala' % index)

        response = self.client.get("/data/%s" % index)
        self.assert200(response)

        response = self.client.get("/data/missing")
        self.assert404(response)

    def test_list_items(self):
        item = Item.create()
        index = 'test'
        item_type = 'album'
        item_data = ItemData.create(item_id=item.id, data_json='{}', data_id='%s/%s/lalala' % (index, item_type))

        response = self.client.get("/data/%s/%s" % (index, item_type))
        self.assert200(response)

        response = self.client.get("/data/%s/missing" % index)
        self.assert404(response)

    def test_data_item(self):
        item = Item.create()
        index = 'test'
        item_type = 'album'
        data_id = 'lalala'
        item_data = ItemData.create(item_id=item.id, data_json='{}', data_id='%s/%s/%s' % (index, item_type, data_id))

        response = self.client.get("/data/%s/%s/%s" % (index, item_type, data_id))
        self.assertEqual(response.status_code, 307)

        response = self.client.get("/data/%s/%s/missing" % (index, item_type))
        self.assert404(response)

