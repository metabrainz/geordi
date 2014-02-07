import collections
import copy
import logging
logger = logging.getLogger('geordi.data.mapping.extract')

class PathTraversalFailure(Exception):
    pass

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
    grouped_path = []
    last_was_choice = True
    tmp = []
    for entry in path:
        if last_was_choice:
            if isinstance(entry, tuple):
                grouped_path.append((True, entry))
            else:
                tmp.append(entry)
                last_was_choice = False
        else:
            if isinstance(entry, tuple):
                grouped_path.append((False, tmp))
                tmp = []
                grouped_path.append((True, entry))
                last_was_choice = True
            else:
                tmp.append(entry)
    if len(tmp) > 0:
        grouped_path.append((False, tmp))
    return _extract_inner(data, grouped_path)

def _extract_inner(data, grouped_path):
    logger.debug('_extract_inner: %r %r', data, grouped_path)
    if len(grouped_path) > 0:
        this_path = grouped_path[0]
        grouped_path = grouped_path[1:]
        if this_path[0]:
            choices = _extract_choice_array(data, this_path[1])
            inners = []
            for choice in choices:
                try:
                    inner_val = _extract_inner(choice[1], copy.copy(grouped_path))
                    inners.append((choice[0], inner_val))
                except PathTraversalFailure as failure:
                    logger.info('A choice (%r) produced nothing internally: %s', choice[0], failure)
            if len(inners) == 0:
                raise PathTraversalFailure('Choice produced no results')
            ret = []
            for choice_pair in inners:
                for previous_value in choice_pair[1]:
                    new_dict = previous_value[0]
                    new_dict.update(choice_pair[0])
                    ret.append((new_dict, previous_value[1]))
            return ret
        else:
            return _extract_inner(_extract_plain_value(data, this_path[1]), grouped_path)
    else:
        return [({}, data)]

def _make_callable(value):
    if not callable(value):
        return lambda *args, **kwargs: value
    else:
        return value

def _extract_choice_array(data, choice):
    logger.debug('_extract_choice_array %r %r', data, choice)
    (name, pred) = choice
    pred = _make_callable(pred)
    if isinstance(data, collections.Mapping):
        all_choices = data.keys()
    elif isinstance(data, collections.Sized):
        all_choices = range(0,len(data))
    else:
        raise PathTraversalFailure('Cannot determine choices for non-dict-like/non-list-like data')
    return [({name: c}, data[c]) for c in all_choices if pred(c)]

def _extract_plain_value(data, path):
    logger.debug('_extract_plain_value %r %r', data, path)
    path = list(path)
    tmp_value = data
    for key in path:
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
    return tmp_value
