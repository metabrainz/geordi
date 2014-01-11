import geordi.data
import json
from flask.ext.script import Manager

data_manager = Manager(usage="Manipulate and query the elasticsearch and postgresql databases.")

@data_manager.command
def show_item(item_id):
    '''Show data for an item given an ID.'''
    print json.dumps(geordi.data.get_item(item_id), indent=4)

@data_manager.command
def show_data_item(data_id):
    '''Show item ID given a data ID.'''
    print geordi.data.data_to_item(data_id)

@data_manager.command
def add_data_item(data_id, data_type, data):
    '''Add or update a data item given a data ID, a type, and the data to use.'''
    print geordi.data.add_data_item(data_id, data_type, data)

@data_manager.command
def delete_data_item(data_id):
    print geordi.data.delete_data_item(data_id)

@data_manager.command
def add_match(item_id, editor, mbid_type, mbid):
    '''Add a match given an item, editor, entity type, and MBID.'''
    print geordi.data.match_item(item_id, editor, mbid_type, mbid)

@data_manager.command
def set_sequences():
    '''Set sequence values back to the max actual value in the table.'''
    print geordi.data.set_sequences()
