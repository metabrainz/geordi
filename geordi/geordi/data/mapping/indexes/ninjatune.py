from __future__ import print_function
from ..rule import Rule
from itertools import chain

def both(dest, *opts, **kwargs):
    prefix = kwargs.get('prefix', [])
    suffix = kwargs.get('suffix', [('index', True)])
    rule_opts = dict([(x, kwargs[x]) for x in kwargs.keys() if x not in ['prefix', 'suffix']])
    return [Rule(prefix + [('r', lambda x, *args, **kwargs: x in opts)] + suffix, dest, **rule_opts)]

def track_name(track, *args, **kwargs):
    title = track.get('MAIN TITLE', track.get('Main Title'))
    title_version = track.get('TITLE VERSION', track.get('Title Version'))
    if title_version:
        return '%s (%s)' % (title, title_version) 
    else:
        return title

ninjatune = {
    'release': list(chain.from_iterable([
                   both(['release', 'title'], 'PRODUCT TITLE', 'Product Title'),
                   both(['release', 'comment'], 'PRODUCT VERSION', 'Product Version'),
                   both(['release', 'artists', 'split', 'names'], 'ARTIST', 'Artist'),
                   both(['release', 'artists', 'unsplit'], 'DISPLAY ARTIST', 'Display Artist'),
                   both(['release', 'barcode'], 'BARCODE', 'Barcode', transform=lambda val, *args, **kwargs: str(int(val))),
                   both(['release', 'release_group'], 'CATALOGUE NUMBER', 'Catalogue Number', link=lambda value, data, *args, **kwargs: 'ninjatune/release/%s:rg' % value, link_only=True),
                   both(['release', 'tag'], 'MAIN GENRE', 'Main Genre', 'SUB_GENRE', 'Sub_Genre', condition=lambda x, *args, **kwargs: x != ''),

                   both(lambda x, *args, **kwargs: ['release', 'mediums', 'split', 'tracks', kwargs.get('t_index'), 'number'], 'TRACK NUMBER', 'track number',
                        prefix=['tracks', ('t_index', True)], suffix=[],
                        transform=lambda val, *args, **kwargs: str(int(val))),
                   [Rule(['tracks', ('t_index', True)],
                        lambda x, *args, **kwargs: ['release', 'mediums', 'split', 'tracks', kwargs.get('t_index'), 'name'],
                        transform=track_name
                    )]
               ]))
}
