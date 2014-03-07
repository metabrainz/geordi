from flask.ext.script import Manager
from geordi import create_app
from geordi.data.manage import data_manager
import json

manager = Manager(create_app)
manager.add_option('-l', '--log-debug', dest='log_debug', required=False, action='store_true')

manager.add_command('data', data_manager)

if __name__ == "__main__":
    manager.run()
