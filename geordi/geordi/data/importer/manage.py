from flask.ext.script import Manager
from ..manage import add_folder
from ..utils import add_data_item
from .indexes import index_setup_functions

import_manager = Manager(usage="Import data to geordi.")

# Each command is an index, and each provides its own arguments; we just need
# to register them all as commands and provide superstructure.
# Thus, each index will export a setup function taking 'add_folder',
# 'add_data_item', and 'import_manager', and it should register a command with
# 'import_manager' for use. It's not unlikely these will be more submanagers.

for func in index_setup_functions:
    func(add_folder, add_data_item, import_manager)
