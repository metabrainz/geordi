import collections
import copy

class PathTraversalFailure(Exception):
    pass

def extract_value(data, path):
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
    if len(grouped_path) > 0:
        this_path = grouped_path[0]
        grouped_path = grouped_path[1:]
        if this_path[0]:
            choices = _extract_choice_array(data, this_path[1])
            inners = [(d[0], _extract_inner(d[1], copy.copy(grouped_path))) for d in choices]
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

def _extract_choice_array(data, choice):
    choice = list(choice)
    if isinstance(data, collections.Mapping):
        all_choices = data.keys()
    elif isinstance(data, collections.Sized):
        all_choices = range(0,len(data))
    else:
        raise PathTraversalFailure('Cannot determine choices for non-dict-like/non-list-like data')
    return [({choice[0]: c}, data[c]) for c in all_choices if choice[1](c)]

def _extract_plain_value(data, path):
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
