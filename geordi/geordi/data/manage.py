import geordi.data
import json
import os
import re
import logging
from flask.ext.script import Manager
from geordi.data.mapping import map_item, verify_map
from geordi.data.model.item import Item
from geordi.data.model.item_data import ItemData

data_manager = Manager(usage="Manipulate and query the elasticsearch and postgresql databases.")

def setup_logger():
    logger = logging.getLogger('geordi')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

@data_manager.command
def show_item(item_id):
    '''Show data for an item given an ID.'''
    print json.dumps(Item.get(item_id).to_dict(), indent=4)

@data_manager.command
def show_data_item(data_id):
    '''Show item ID given a data ID.'''
    print ItemData.data_to_item(data_id)

@data_manager.command
def show_item_map(item_id):
    item = Item.get(item_id).to_dict()
    data = map_item(item)
    print json.dumps({'data': data[0], 'links': data[1]}, indent=4)

@data_manager.command
def verify_map(map_data_filename):
    with open(map_data_filename) as f:
        data = json.load(f)
    print list(verify_map(data))

@data_manager.command
def add_data_item(data_id, data_type, data_filename):
    '''Add or update a data item given a data ID, a type, and the data to use.'''
    with open(data_filename) as f:
        data = f.read()
    item_id = geordi.data.add_data_item(data_id, data_type, data)
    print json.dumps(Item.get(item_id).to_dict(), indent=4)

@data_manager.command
def add_folder(folder):
    '''Add a whole folder. Should be organized by expected data ID, e.g.
       <folder name>/discogs/artist/5.json becomes data item 'discogs/artist/5'
    '''
    indices = sorted(os.listdir(folder))
    for index in indices:
        item_types = sorted(os.listdir(folder + '/' + index))
        for item_type in item_types:
            items = sorted(os.listdir(folder + '/' + index + '/' + item_type))
            if '_itemtype' in items:
                with open('%s/%s/%s/_itemtype' % (folder, index, item_type)) as f:
                    data_type = f.read().strip()
                items = [item for item in items if item != '_itemtype']
            else:
                data_type = item_type
            print "Using data type '%s' for %s/%s" % (data_type, index, item_type)
            for item in items:
                if re.search('.json$',item):
                    basename = re.sub('.json$', '', item)
                    print "> Adding %s/%s/%s as %s/%s/%s" % (index, item_type, item, index, item_type, basename)
                    add_data_item('%s/%s/%s' % (index, item_type, basename), data_type, '%s/%s/%s/%s' % (folder, index, item_type, item))
                else:
                    print ">> File %s/%s/%s not a .json file, skipping" % (index, item_type, item)

@data_manager.command
def delete_data_item(data_id):
    print geordi.data.delete_data_item(data_id)

@data_manager.command
def set_sequences():
    '''Set sequence values back to the max actual value in the table.'''
    print geordi.data.set_sequences()

from geordi.data.importer.manage import import_manager
data_manager.add_command('import', import_manager)
