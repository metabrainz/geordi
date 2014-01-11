from flask.ext.script import Manager
from geordi import create_app
import geordi.data
import json

manager = Manager(create_app())

@manager.command
def item(item_id):
    print json.dumps(geordi.data.get_item(item_id), indent=4)

@manager.command
def data(data_id):
    print geordi.data.data_to_item(data_id)

@manager.command
def add_data(data_id, data_type, data):
    print geordi.data.add_data(data_id, data_type, data)

if __name__ == "__main__":
    manager.run()
