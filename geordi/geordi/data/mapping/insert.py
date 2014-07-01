import collections
import logging
import copy
from .pathutils import make_callable, no_op_value

logger = logging.getLogger('geordi.data.mapping.insert')

class InvalidInsertion(Exception):
    pass

def fix_path(path):
    ins = PathInserter({})
    path = ins._process_path(path)
    return [entry.source_value() for entry in path]

class PathInserter(object):
    def __init__(self, data):
        self.data = data

    def insert_data(self, path, value):
        path = self._process_path(path)
        tmp = copy.deepcopy(self.data)
        for part in path:
            tmp = part.prepare(tmp)

        if tmp is None:
            supr = value
        elif isinstance(tmp, list):
            logger.warning("Inserting to something that's already a list (%s) is deprecated", tmp)
            tmp.append(value)
            supr = tmp
        else:
            raise InvalidInsertion('Attempt to insert at an invalid point in a structure.')

        for part in reversed(path):
            supr = part.insert(supr)

        self.data = supr
    
    def get_data(self):
        return self.data

    def _process_path(self, path):
        final = []
        for entry in path:
            if isinstance(entry, tuple):
                final.append(OrderedPathPart(*entry))
            elif isinstance(entry, PathPart):
                final.append(entry)
            else:
                final.append(SimplePathPart(entry))
        if not (isinstance(path[-1], tuple) or isinstance(path[-1], PathPart)):
            logger.debug("Inserting an OrderedPathPart since %s is neither tuple nor PathPart", path[-1])
            final.append(OrderedPathPart())
        logger.debug("Final path is %r", final)
        return final

class PathPart(object):
    def __init__(self, before=no_op_value, after=no_op_value, no_manip=False):
        self.before = make_callable(before)
        self.after = make_callable(after)
        self.no_manip = no_manip
        
    def prepare(self, data):
        raise Exception('unimplemented')

    def insert(self, supr):
        raise Exception('unimplemented')

    def source_value(self):
        raise Exception('unimplemented')

class SimplePathPart(PathPart):
    def __init__(self, key, **kwargs):
        self.key = key
        super(SimplePathPart, self).__init__(**kwargs)

    def __repr__(self):
        return '<SimplePathPart %s>' % self.key
    def __str__(self):
        return self.source_value(no_manip_override=False)

    def source_value(self, no_manip_override=None):
        no_manip = self.no_manip
        if no_manip_override is not None: no_manip = no_manip_override
        if not no_manip:
            return self.key
        else:
            return self

    def prepare(self, data):
        logger.info('SimplePathPart.prepare (%s) %r', self.key, data)
        if data is None:
            self.data = None
            return None
        elif isinstance(data, collections.Mapping):
            self.data = data
            return data.get(self.key)
        elif isinstance(data, list):
            logger.warning("Inserting to something that's already a list (%s) is deprecated", data)
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
            logger.warning("Inserting to something that's already a list (%s) is deprecated", self.data)
            if len(self.data) <= self.key:
                self.data.extend([None for i in range(-1,self.key-len(self.data))])
            self.data[self.key] = supr
            return self.data
        else:
            raise InvalidInsertion('Cannot insert data to things that are neither None, a mapping, or a list. Got %r' % data)

class OrderedPathPart(PathPart):
    def __init__(self, ordering=None, identifier=None, **kwargs):
        self.ordering = ordering
        self.identifier = identifier
        if identifier is None and ordering is not None:
            self.identifier = ordering
        super(OrderedPathPart, self).__init__(**kwargs)

    def __repr__(self):
        return '<OrderedPathPart (%s, %s)>' % (self.ordering, self.identifier)

    def source_value(self):
        return (self.ordering, self.identifier)

    def prepare(self, data):
        logger.info('OrderedPathPart.prepare (%s, %s) %r', self.ordering, self.identifier , data)
        if not (isinstance(data, list) or data is None):
            raise InvalidInsertion('Cannot insert an ordered element to things other than lists/None. Got %r' % data)
        elif isinstance(data, list):
            if len([True for item in data if not isinstance(item, tuple)]) > 0:
                raise InvalidInsertion('Attempt to insert an ordering tuple to a list with non-ordered values: %r' % data)
            self.data = data
            for item in data:
                if item[2] == self.identifier and self.identifier is not None:
                    if self.ordering is not None and item[1] != self.ordering:
                        raise InvalidInsertion('Bad identifier/ordering: provided identifier %s has ordering %s, but we were given ordering %s' % (self.identifier, item[1], self.ordering))
                    return item[0]
            return None
        else:
            self.data = []
            return None

    def insert(self, supr):
        logger.info('OrderedPathPart.insert (%s, %s) %r', self.ordering, self.identifier , supr)
        if not isinstance(self.data, list):
            raise InvalidInsertion('Cannot insert an ordered element to things other than lists. Got %r' % self.data)
        else:
            if len([True for item in self.data if not isinstance(item, tuple)]) > 0:
                raise InvalidInsertion('Attempt to insert an ordering tuple to a list with non-ordered values: %r' % self.data)
            if self.identifier is not None:
                self.inserted = False
                ret = [self._insert_item(item, supr) for item in self.data]
                if not self.inserted:
                    ret.append((supr, self.ordering, self.identifier))
                return ret
            else:
                ret = self.data
                ret.append((supr, self.ordering, self.identifier))
                return ret

    def _insert_item(self, item, supr):
        (current, ordering, identifier) = item
        if not self.inserted and identifier == self.identifier:
            if self.ordering is not None and ordering != self.ordering:
                raise InvalidInsertion('Bad identifier/ordering: provided identifier %s has ordering %s, but we were given ordering %s' % (self.identifier, ordering, self.ordering))
            self.inserted = True
            return (supr, ordering, identifier)
        elif self.inserted and identifier == self.identifier:
            raise InvalidInsertion('Duplicate identifier: %s', identifier)
        else:
            return item

def insert_value(data, path, value):
    inserter = PathInserter(data)
    inserter.insert_data(path, value)
    return inserter.get_data()
