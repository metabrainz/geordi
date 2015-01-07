import os
import sys
import json


def entity2json(entity):
    return json.dumps(entity, separators=(',', ':'), sort_keys=True)

def is_list(value):
    return isinstance(value, (list, tuple))

def bbc_setup(add_folder, add_data_item, import_manager):
    def add_artist(artist):
        print add_data_item('bbc/artist/' + str(artist['id']), 'artist', entity2json(artist))

    def add_work(work):
        print add_data_item('bbc/work/' + str(work['id']), 'work', entity2json(work))

    def _import_bbc_json(json_file):
        if not json_file.endswith('.json'):
            print 'Skipping non-JSON file ' + json_file
            return

        try:
            json_data = json.load(open(json_file, 'r'))
        except Exception as e:
            print 'Skipping %s: %s: %s' % (json_file, type(e).__name__, e)
            return

        if is_list(json_data):
            print 'Processing ' + json_file

            for work in json_data:
                if 'composer' in work:
                    add_artist(work['composer'])
                add_work(work)
        else:
            print 'Skipping %s: JSON data is not a list at top level.' % json_file

    @import_manager.command
    def bbc(path):
        """Import JSON from BBC Proms data."""
        if os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file_name in files:
                    _import_bbc_json(os.path.join(root, file_name))
        else:
            _import_bbc_json(path)
