import re
from ..rule import Rule

def make_artist_name(val, data, *args, **kwargs):
    names = []
    for prop in ['name_prefix', 'first_names', 'last_name']:
        if data.get(prop) and data[prop] != '':
            names.append(data[prop])
    if len(names) > 0:
        return " ".join(names)
    else:
        return ""

bbc_index = {
    'artist': [
        Rule(['first_names'], ['artist', 'name'], transform=make_artist_name)
    ],
    'work': [
        Rule(['name'], ['work', 'name'])
    ]
}
