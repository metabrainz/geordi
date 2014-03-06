import collections
import logging

logger = logging.getLogger('geordi.data.mapping.insert')

class InvalidInsertion(Exception):
    pass

def insert_value(data, path, value):
    '''Inserts data. Always to arrays.'''
    logger.debug('insert_value %r %r %r', data, path, value)
    if len(path) == 0:
        if data is None:
            return [value]
        elif isinstance(data, list):
            data.append(value)
            return data
        else:
            raise InvalidInsertion('Attempt to insert at an invalid point in a structure.')
    else:
        this_key = path[0]
        path = path[1:]
        if data is None:
            if isinstance(this_key, int):
                ret_list = [None for i in range(-1,this_key)]
                ret_list[this_key] = insert_value(None, path, value)
                return ret_list
            else:
                return {this_key: insert_value(None, path, value)}
        elif isinstance(data, collections.Mapping):
            data[this_key] = insert_value(data.get(this_key), path, value)
            return data
        elif isinstance(data, list):
            if len(data) <= this_key:
                data.extend([None for i in range(-1,this_key-len(data))])
            data[this_key] = insert_value(data[this_key], path, value)
            return data
        else:
            raise InvalidInsertion('Attempt to insert to something other than None, a mapping, or a list')
