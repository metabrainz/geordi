import collections
import copy
import logging
logger = logging.getLogger('geordi.data.mapping.extract')

from .pathutils import make_callable, no_op_value

class PathTraversalFailure(Exception):
    pass

class PathExtractor(object):
    def __init__(self, path):
        self.path = self._process_path(path)

    def process_data(self, data):
        produced = [({}, data)]
        for part in self.path:
            produced = part.produce_values(produced)
        return produced

    def _process_path(self, path):
        grouped_path = []
        last_was_choice = True
        tmp = []
        for entry in path:
            if last_was_choice:
                if isinstance(entry, tuple):
                    grouped_path.append(_tuple_to_choice(entry))
                elif isinstance(entry, PathPart):
                    grouped_path.append(entry)
                else:
                    tmp.append(entry)
                    last_was_choice = False
            else:
                if isinstance(entry, tuple) or isinstance(entry, PathPart):
                    grouped_path.append(PlainPathPart(tmp))
                    tmp = []
                    if isinstance(entry, tuple):
                        grouped_path.append(_tuple_to_choice(entry))
                    else:
                        grouped_path.append(entry)
                    last_was_choice = True
                else:
                    tmp.append(entry)
        if len(tmp) > 0:
            grouped_path.append(PlainPathPart(tmp))
        logger.debug("Final path is %r", grouped_path)
        return grouped_path

class PathPart(object):
    def __init__(self, before=no_op_value, after=no_op_value):
        self.before = make_callable(before)
        self.after = make_callable(after)

    def produce_values(self, data):
        logger.info('PathPart.produce_values %r', data)
        values = []
        for value in data:
            try:
                vals = self.produce_value((value[0], self.before(value[1])))
                values.extend([(val[0], self.after(val[1])) for val in vals])
            except PathTraversalFailure as failure:
                logger.info('A choice (%r) produced nothing internally: %s', value[0], failure)
        if len(values) == 0:
            raise PathTraversalFailure('No results from any choice made thus far.')
        return values

    def produce_value(self, item):
        raise Exception('Unimplemented.')

class PlainPathPart(PathPart):
    def __init__(self, keys, **kwargs):
        self.keys = keys
        super(PlainPathPart, self).__init__(**kwargs)

    def __repr__(self):
        return '<PlainPathPart %s>' % self.keys

    def produce_value(self, item):
        logger.info('PlainPathPart.produce_value (%s) %r', self.keys, item)
        tmp_value = item[1]
        for key in self.keys:
            if isinstance(tmp_value, collections.Mapping):
                if key in tmp_value:
                    tmp_value = tmp_value[key]
                else:
                    raise PathTraversalFailure('Missing key in dict-like data')
            elif isinstance(tmp_value, collections.Sized) and isinstance(key, int):
                if len(tmp_value) > key:
                    tmp_value = tmp_value[key]
                else:
                    raise PathTraversalFailure('Missing key in list-like data')
            else:
                raise PathTraversalFailure('Data is neither mapping nor sized, or key for list-like data is not integer')
        return [(item[0], tmp_value)]

class ChoicePathPart(PathPart):
    def __init__(self, name, condition, **kwargs):
        self.name = name
        self.condition = make_callable(condition)
        self.has_before = kwargs.get('before')  # really only needs truthy or falsy, but eh
        super(ChoicePathPart, self).__init__(**kwargs)

    def __repr__(self):
        if self.has_before:
            return '<ChoicePathPart (%s, %s, %s)>' % (self.name, self.condition, self.before)
        else:
            return '<ChoicePathPart (%s, %s)>' % (self.name, self.condition)

    def produce_value(self, item):
        logger.info('ChoicePathPart.produce_value (%s) %r', self.name, item)
        if isinstance(item[1], collections.Mapping):
            all_choices = item[1].keys()
        elif isinstance(item[1], collections.Sized):
            all_choices = range(0,len(item[1]))
        else:
            raise PathTraversalFailure('Cannot determine choices for non-dict-like/non-list-like data')
        values = []
        for c in all_choices:
            if self.condition(c):
                new_dict = copy.copy(item[0])    
                new_dict[self.name] = c
                values.append((new_dict, item[1][c]))
        return values

def _tuple_to_choice(choice_tuple):
    if len(choice_tuple) > 2:
        choice = ChoicePathPart(choice_tuple[0], choice_tuple[1], before=choice_tuple[2])
    else:
        choice = ChoicePathPart(choice_tuple[0], choice_tuple[1])
    return choice

def extract_value(data, path):
    '''
    Extract a value from a JSON data structure by path.

    Paths are defined as arrays comprised of indexes into structures (string or
    integer) or choice definitions. Plain indexes specify exactly where to go
    next within the data structure; an error will be raised in the case of
    missing or string indexes to list-like structures (integer indexes for
    dict-like structures, while less common, are not invalid).

    Choice definitions are tuples of a descriptive name for the choice, and a
    function of one argument that serves as a predicate for which choices should
    be followed. The one argument provided is the immediate index of the possible
    choice to be considered. That is, a choice of ('bar', lambda a: a > 0)
    specifies that all values that correspond to indexes of 1 or greater (probably
    in a list-like structure) should be returned.

    This function will always return an array of (choices, value) tuples, where
    'choices' will be a dictionary of choices by name mapped to what choice corresponds
    to the particular value returned. (When no choices are made by a path, the return value
    will therefore be [({}, value)]).

    For example, given the data:
    {
     'foo': {
       'bar': [
          {'baz': 'quux'},
          {'baz': 'quuy'},
          {'baz': 'quuz'}
       ]
     }
    }
    and the path ['foo', 'bar', ('bar_index', lambda a: a > 0), 'baz'], this function
    will produce
    [({'bar_index': 1}, 'quuy'), ({'bar_index': 2}, 'quuz')]

    Errors will raise PathTraversalFailure with a descriptive message.
    '''
    logger.debug('extract_value %r %r', data, path)
    extractor = PathExtractor(path)
    return extractor.process_data(data)
