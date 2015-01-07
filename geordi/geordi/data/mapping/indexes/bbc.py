import re
from ..rule import Rule
from ..insert import SimplePathPart


def make_artist_name(**kwargs):
    prefix = kwargs.get('prefix')
    def closure(val, data, *args, **kwargs):
        if prefix is not None and prefix in data:
            data = data[prefix]
        names = []
        for prop in ['name_prefix', 'first_names', 'last_name']:
            if data.get(prop) and data[prop] != '':
                names.append(data[prop])
        if len(names) > 0:
            return " ".join(names)
        else:
            return ""

    return closure

bbc_index = {
    'artist': [
        Rule(['first_names'], ['artist', 'name'], transform=make_artist_name())
    ],
    'work': [
        Rule(['name'], ['work', 'name']),
        Rule(
            ['composer', 'first_names'],
            lambda *args, **kwargs: ['work', 'composers', (kwargs.get('index'),), SimplePathPart('target', no_manip=True)],
            transform=make_artist_name(prefix='composer'),
            link=lambda value, data, *args, **kwargs: 'bbc/artist/%s' % data['composer']['id'],
        )
    ]
}
