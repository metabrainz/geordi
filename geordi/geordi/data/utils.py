from model import db
from model.item import Item
from model.item_data import ItemData
from model.item_link import ItemLink
from .mapping import map_item, verify_map
import json
import re

def get_renderable(item_id):
    '''Fetch and return an item's data including a pretty-printed version of the data items.'''
    item = Item.get(item_id)
    if item is not None:
        item = item.to_dict()
        item['data_formatted'] = dict([(d_id, json.dumps(data, indent=4)) for d_id, data in item.get('data', {}).iteritems()])
        item['map_formatted'] = json.dumps(item['map'], indent=4)
    return item

def add_data_item(data_id, data_type, data):
    '''Add or update a data item given an ID, type, and data. Create a new item, for additions.'''
    item_id = original_item_id = ItemData.data_to_item(data_id)
    if item_id is None:
        item_id = _create_item(data_type)
    _register_data_item(item_id, data_id, data, update=original_item_id)
    _map_item(item_id)
    db.session.commit()
    return item_id

def delete_data_item(data_id):
    ItemData.delete_data_item(data_id)
    db.session.commit()

def set_sequences():
    '''Set sequence values back to the max actual value in the tables.'''
    from model import db
    result = db.session.execute("select coalesce(max(id),0) + 1 from item")
    (restart,) = result.fetchone()
    db.session.execute("ALTER SEQUENCE item_id_seq RESTART %s", (restart,))
    db.session.commit()

def _create_item(data_type):
    item = Item.create(type=data_type)
    if not item.id:
        raise Exception('No row created')
    return item.id

link_type_map = {
    'release%artists': 'artist',
    'release%release_group': 'release_group',
    'release%events': 'area',
    'release%labels': 'label',

    'release%mediums%combined%%tracks%%recording': 'recording',
    'release%mediums%combined%%tracks%%artists': 'artist',
    'release%mediums%split%tracks%%recording': 'recording',
    'release%mediums%split%tracks%%artists': 'artist',
}
def _link_type_to_item_type(link_type):
    '''First try the whole path, then take off the last element, etc.,
       until one matches in link_type_map, or return None.'''
    path = re.sub('%[0-9]+(%|$)', '%\\1', link_type).split('%')
    for i in range(len(path),0,-1):
        prospect = link_type_map.get('%'.join(path[:i]))
        if prospect is not None:
            return prospect
    return None

def _map_item(item_id):
    # fetch data
    item = Item.get(item_id)
    # generate map
    (mapped, links) = map_item(item.to_dict())
    this_mapped = mapped[None]
    if list(verify_map(this_mapped)):
        print "Validation errors in mapping item %s: %r, continuing." % (item_id, list(verify_map(this_mapped)))
    # First, update this item's map
    item.map = json.dumps(this_mapped, separators=(',', ':'))
    db.session.flush()
    # Then, go through the links, creating items as needed with the types designated by their mapping paths
    ItemLink.delete_by_item_id(item_id)
    for (node, destination, data_id) in links:
        link_type = '%'.join([str(d) for d in destination])
        if node is None:
            node_item = item_id
        else:
            node_item = ItemData.data_to_item(node)
        target_item = ItemData.data_to_item(data_id)
        if target_item is None:
            target_item = _create_item(_link_type_to_item_type(link_type))
            print "%s -> %s" % (data_id, target_item)
            _register_data_item(target_item, data_id, '{}')
        if node_item is None:
            node_item = _create_item('')
            print "%s -> %s" % (node, node_item)
            _register_data_item(node_item, node, '{}')
        ItemLink.find_or_insert(node_item, target_item, link_type)
    # Now that we can be assured any types set by links are already set on the items, insert the maps for other mapped nodes
    for data_id in mapped.keys():
        if data_id is not None:
            verify = list(verify_map(mapped[data_id]))
            if verify:
                print "Validation errors in mapping data item %s: %r, continuing" % (data_id, verify)
            add_data_item(data_id, '', json.dumps(mapped[data_id]))

def _register_data_item(item_id, data_id, data, update=False):
    if not update:
        ItemData.create(item_id, data, data_id)
    else:
        ItemData.update(item_id, data, data_id)

#def get_entities(mbid_or_mbids, conn=None, cached=True, type_hint=None):
#    entities = []
#    if isinstance(mbid_or_mbids, basestring):
#        mbids = [mbid_or_mbids]
#        one_result = True
#    else:
#        mbids = mbid_or_mbids
#        one_result = False
#    if conn is None:
#        conn = get_db()
#    with conn.cursor() as curs:
#        if cached:
#            curs.execute('SELECT mbid, type, data FROM entity WHERE mbid = any(%s)', (mbids,))
#            if curs.rowcount > 0:
#                for row in curs.fetchall():
#                    (mbid, mbidtype, data) = row
#                    entity = json.loads(data)
#                    entity['mbid'] = mbid
#                    entity['type'] = mbidtype
#                    entities.push(entity)
#        pass
#    if one_result and len(entities) == 1:
#        return entities[0]
#    elif not one_result:
#        return entities
#    elif len(entities) > 1:
#        raise Exception('More than one result fetching entities, when one expected')
