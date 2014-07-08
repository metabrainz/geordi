from geordi.test_case import GeordiTestCase
from geordi.data.model.item import Item
from geordi.data.model.item_data import ItemData


class APIViewsTestCase(GeordiTestCase):

    def test_item(self):
        item = Item.create()

        response = self.client.get("/api/1/item/%s" % item.id, environ_base={'REMOTE_ADDR': '127.0.0.1'})
        self.assert200(response)
        response = self.client.get("/api/1/item/0%s" % item.id, environ_base={'REMOTE_ADDR': '127.0.0.1'})
        self.assert200(response)
        self.assertEquals(response.json, item.to_dict())

        response = self.client.get("/api/1/item/%s0" % item.id, environ_base={'REMOTE_ADDR': '127.0.0.1'})
        self.assert404(response)
        response = self.client.get("/api/1/item/missing", environ_base={'REMOTE_ADDR': '127.0.0.1'})
        self.assert404(response)

    def test_list_indexes(self):
        response = self.client.get("/api/1/data", environ_base={'REMOTE_ADDR': '127.0.0.1'})
        self.assert200(response)
        self.assertEquals(response.json, dict(indexes=[]))

    def test_list_index(self):
        item = Item.create()
        index = 'test'
        item_data = ItemData.create(item_id=item.id, data_json='{}', data_id='%s/album/lalala' % index)

        response = self.client.get("/api/1/data/%s" % index, environ_base={'REMOTE_ADDR': '127.0.0.1'})
        self.assert200(response)
        self.assertEquals(response.json, dict(index=index, item_types=ItemData.get_item_types_by_index(index)))

        response = self.client.get("/api/1/data/missing", environ_base={'REMOTE_ADDR': '127.0.0.1'})
        self.assert404(response)

    def test_list_items(self):
        item = Item.create()
        index = 'test'
        item_type = 'album'
        item_data = ItemData.create(item_id=item.id, data_json='{}', data_id='%s/%s/lalala' % (index, item_type))

        response = self.client.get("/api/1/data/%s/%s" % (index, item_type), environ_base={'REMOTE_ADDR': '127.0.0.1'})
        self.assert200(response)
        self.assertEquals(response.json, dict(index=index, item_type=item_type,
                                              items=ItemData.get_item_ids(index, item_type)))

        response = self.client.get("/api/1/data/%s/missing" % index, environ_base={'REMOTE_ADDR': '127.0.0.1'})
        self.assert404(response)

    def test_data_item(self):
        item = Item.create()
        index = 'test'
        item_type = 'album'
        data_id = 'lalala'
        item_data = ItemData.create(item_id=item.id, data_json='{}', data_id='%s/%s/%s' % (index, item_type, data_id))

        response = self.client.get("/api/1/data/%s/%s/%s" % (index, item_type, data_id), environ_base={'REMOTE_ADDR': '127.0.0.1'})
        self.assert200(response)
        self.assertEquals(response.json, dict(
            index=index, item_type=item_type,
            data_id=data_id, item_id=ItemData.data_to_item('/'.join([index, item_type, data_id]))))

        response = self.client.get("/api/1/data/%s/%s/missing" % (index, item_type), environ_base={'REMOTE_ADDR': '127.0.0.1'})
        self.assert404(response)

