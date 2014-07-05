from __future__ import print_function
from ..rule import Rule
from itertools import chain
from ..insert import SimplePathPart
import re

def both(dest, *opts, **kwargs):
    prefix = kwargs.get('prefix', [])
    suffix = kwargs.get('suffix', [('index', True)])
    condition = kwargs.get('condition', lambda x, *args, **kwargs: x != '')
    rule_opts = dict([(x, kwargs[x]) for x in kwargs.keys() if x not in ['prefix', 'suffix', 'condition']])
    return [Rule(prefix + [('r', lambda x, *args, **kwargs: x in opts)] + suffix, dest, condition=condition, **rule_opts)]

def track_name(track, *args, **kwargs):
    title = track.get('MAIN TITLE', track.get('Main Title'))
    title_version = track.get('TITLE VERSION', track.get('Title Version'))
    if title_version:
        return '%s (%s)' % (title, title_version) 
    else:
        return title

ninjatune = {
    'release': list(chain.from_iterable([
                   both(['release', 'name'], 'PRODUCT TITLE', 'Product Title'),
                   both(['release', 'comment'], 'PRODUCT VERSION', 'Product Version'),

                   both(lambda *args, **kwargs: ['release', 'artists', 'split', 'names', (kwargs.get('index'),)], 'ARTIST', 'Artist', suffix=[('i2', True), ('index', True, lambda val, *args, **kwargs: val.split('|'))],
                        link=lambda value, *args, **kwargs: 'ninjatune/artist/%s' % value.strip()),
                   both(['release', 'artists', 'unsplit'], 'DISPLAY ARTIST', 'Display Artist'),

                   both(lambda x, *args, **kwargs: ['release', 'labels', 'combined', (kwargs.get('index'),), SimplePathPart('label', no_manip=True)], 'MAIN LABEL', 'Main Label',
                        link=lambda value, *args, **kwargs: 'ninjatune/label/%s' % value.strip()),
                   both(lambda x, *args, **kwargs: ['release', 'labels', 'combined', (kwargs.get('index'),), SimplePathPart('catalog_number', no_manip=True)], 'CATALOGUE NUMBER', 'Catalogue Number'),
                   both(lambda x, *args, **kwargs: ['release', 'labels', 'combined', (kwargs.get('index')+1,), SimplePathPart('label', no_manip=True)], 'SUB_LABEL', 'Sub_Label',
                        link=lambda value, *args, **kwargs: 'ninjatune/label/%s' % value.strip()),
                   both(lambda x, *args, **kwargs: ['release', 'labels', 'combined', (kwargs.get('index')+1,), SimplePathPart('catalog_number', no_manip=True)], 'CATALOGUE NUMBER', 'Catalogue Number'),

                   both(['release', 'barcode'], 'BARCODE', 'Barcode', transform=lambda val, *args, **kwargs: str(int(str(val).strip())), condition=lambda x, *args, **kwargs: re.match('^\s*[0-9]+\s*$', str(x))),
                   both(['release', 'tag'], 'MAIN GENRE', 'Main Genre', 'SUB_GENRE', 'Sub_Genre', condition=lambda x, *args, **kwargs: x != ''),

                   both(lambda x, *args, **kwargs: ['release', 'mediums', 'split', 'tracks', (kwargs.get('t_index'),), 'number'], 'TRACK NUMBER', 'track number',
                        prefix=['tracks', ('t_index', True)], suffix=[],
                        transform=lambda val, *args, **kwargs: str(int(val))),
                   both(lambda x, *args, **kwargs: ['release', 'mediums', 'split', 'tracks', (kwargs.get('t_index'),), 'artists', 'split', 'names', (kwargs.get('index'),)], '_ARTIST', '_Artist',
                        prefix=['tracks', ('t_index', True)], suffix=[('index', True, lambda val, *args, **kwargs: val.split('|'))],
                        link=lambda value, *args, **kwargs: 'ninjatune/artist/%s' % value.strip()),
                   both(lambda x, *args, **kwargs: ['release', 'mediums', 'split', 'tracks', (kwargs.get('t_index'),), 'artists', 'unsplit'], '_DISPLAY ARTIST', '_Display Artist',
                        prefix=['tracks', ('t_index', True)], suffix=[]),
                   [Rule(['tracks', ('t_index', True)],
                        lambda x, *args, **kwargs: ['release', 'mediums', 'split', 'tracks', (kwargs.get('t_index'),), 'name'],
                        transform=track_name
                    ),
                    Rule(['tracks', ('t_index', True)],
                        lambda x, *args, **kwargs: ['release', 'mediums', 'split', 'tracks', (kwargs.get('t_index'),), 'recording'],
                        transform=track_name,
                        link=lambda value, data, *args, **kwargs: 'ninjatune/release/%s:recording-%s' % (data.get('CATALOGUE NUMBER', data.get('Catalogue Number'))[0],kwargs.get('t_index')),
                    )
                   ],

                   both(['recording', 'isrcs'], 'ISRC CODE', 'ISRC Code',
                        prefix=['tracks', ('t_index', True)], suffix=[],
                        transform=lambda val, *args, **kwargs: val.replace('-', ''),
                        node_destination=lambda val, *args, **kwargs: 'recording-%s' % kwargs.get('t_index')),
                   [
                    Rule(['tracks', ('t_index', True)],
                        lambda x, *args, **kwargs: ['recording', 'name'],
                        transform=track_name,
                        node_destination=lambda val, *args, **kwargs: 'recording-%s' % kwargs.get('t_index')
                    )
                   ]
               ]))
}
