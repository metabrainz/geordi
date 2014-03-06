import collections
import logging
import copy
from .pathutils import make_callable, no_op_value

logger = logging.getLogger('geordi.data.mapping.insert')

class InvalidInsertion(Exception):
    pass

class PathInserter(object):
    def __init__(self, data):
        self.data = data

    def insert_data(self, path, value):
        path = self._process_path(path)
        tmp = copy.deepcopy(self.data)
        for part in path:
            tmp = part.prepare(tmp)

        if tmp is None:
            supr = [value]
        elif isinstance(tmp, list):
            tmp.append(value)
            supr = tmp
        else:
            raise InvalidInsertion('Attempt to insert at an invalid point in a structure.')

        for part in reversed(path):
            supr = part.insert(supr)

        self.data = supr
    
    def _process_path(self, path):
        return [SimplePathPart(k) for k in path]

class PathPart(object):
    def __init__(self, before=no_op_value, after=no_op_value):
        self.before = make_callable(before)
        self.after = make_callable(after)
        
    def prepare(self, data):
        raise Exception('unimplemented')

    def insert(self, supr):
        raise Exception('unimplemented')

class SimplePathPart(object):
    def __init__(self, key, **kwargs):
        self.key = key
        super(SimplePathPart, self).__init__(**kwargs)

    def __repr__(self):
        return '<SimplePathPart %s>' % self.key

    def prepare(self, data):
        logger.info('SimplePathPart.prepare (%s) %r', self.key, data)
        if data is None:
            self.data = None
            return None
        elif isinstance(data, collections.Mapping):
            self.data = data
            return data.get(self.key)
        elif isinstance(data, list):
            self.data = data
            if len(data) <= self.key:
                return None
            else:
                return data[self.key]
        else:
            raise InvalidInsertion('Cannot insert data to things that are neither None, a mapping, or a list. Got %r' % data)

    def insert(self, supr):
        logger.info('SimplePathPart.insert (%s) %r', self.key, supr)
        if self.data is None:
            if isinstance(self.key, int):
                ret = [None for i in range(-1,self.key)]
                ret[self.key] = supr
                return ret
            else:
                return {self.key: supr}
        elif isinstance(self.data, collections.Mapping):
            self.data[self.key] = supr
            return self.data
        elif isinstance(self.data, list):
            if len(self.data) <= self.key:
                self.data.extend([None for i in range(-1,self.key-len(self.data))])
            self.data[self.key] = supr
            return self.data
        else:
            raise InvalidInsertion('Cannot insert data to things that are neither None, a mapping, or a list. Got %r' % data)

def insert_value(data, path, value):
    inserter = PathInserter(data)
    inserter.insert_data(path, value)
    return inserter.data
