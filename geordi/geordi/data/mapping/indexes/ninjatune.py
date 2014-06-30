from __future__ import print_function
from ..rule import Rule
from itertools import chain
from ..insert import SimplePathPart

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
                        link=lambda value, *args, **kwargs: 'ninjatune/artist/%s' % value),
                   both(['release', 'artists', 'unsplit'], 'DISPLAY ARTIST', 'Display Artist'),

                   both(lambda x, *args, **kwargs: ['release', 'labels', 'combined', (kwargs.get('index'),), SimplePathPart('label', no_manip=True)], 'MAIN LABEL', 'Main Label',
                        link=lambda value, *args, **kwargs: 'ninjatune/label/%s' % value),
                   both(lambda x, *args, **kwargs: ['release', 'labels', 'combined', (kwargs.get('index'),), SimplePathPart('catalog_number', no_manip=True)], 'CATALOGUE NUMBER', 'Catalogue Number'),
                   both(lambda x, *args, **kwargs: ['release', 'labels', 'combined', (kwargs.get('index')+1,), SimplePathPart('label', no_manip=True)], 'SUB_LABEL', 'Sub_Label',
                        link=lambda value, *args, **kwargs: 'ninjatune/label/%s' % value),
                   both(lambda x, *args, **kwargs: ['release', 'labels', 'combined', (kwargs.get('index')+1,), SimplePathPart('catalog_number', no_manip=True)], 'CATALOGUE NUMBER', 'Catalogue Number'),

                   # Release events
                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'Main'), SimplePathPart('date', no_manip=True)], 'Main Release Date', 'Main Release date',
                        transform=lambda val, *args, **kwargs: '-'.join([str(x) for x in val[0:3]]),
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),

                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'UK'), SimplePathPart('date', no_manip=True)], 'UK Release Date', 'UK Release date',
                        transform=lambda val, *args, **kwargs: '-'.join([str(x) for x in val[0:3]]),
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),
                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'UK'), SimplePathPart('country', no_manip=True)], 'UK Release Date', 'UK Release date',
                        transform='UK',
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),

                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'US'), SimplePathPart('date', no_manip=True)], 'US Release Date', 'US Release date',
                        transform=lambda val, *args, **kwargs: '-'.join([str(x) for x in val[0:3]]),
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),
                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'US'), SimplePathPart('country', no_manip=True)], 'US Release Date', 'US Release date',
                        transform='US',
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),

                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'DE'), SimplePathPart('date', no_manip=True)], 'Germany Release Date', 'Germany Release date',
                        transform=lambda val, *args, **kwargs: '-'.join([str(x) for x in val[0:3]]),
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),
                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'DE'), SimplePathPart('country', no_manip=True)], 'Germany Release Date', 'Germany Release date',
                        transform='DE',
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),

                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'FR'), SimplePathPart('date', no_manip=True)], 'France Release Date', 'France Release date',
                        transform=lambda val, *args, **kwargs: '-'.join([str(x) for x in val[0:3]]),
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),
                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'FR'), SimplePathPart('country', no_manip=True)], 'France Release Date', 'France Release date',
                        transform='FR',
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),

                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'AU'), SimplePathPart('date', no_manip=True)], 'Australia Release Date', 'Australia Release date',
                        transform=lambda val, *args, **kwargs: '-'.join([str(x) for x in val[0:3]]),
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),
                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'AU'), SimplePathPart('country', no_manip=True)], 'Australia Release Date', 'Australia Release date',
                        transform='AU',
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),

                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'JP'), SimplePathPart('date', no_manip=True)], 'Japan Release Date', 'Japan Release date',
                        transform=lambda val, *args, **kwargs: '-'.join([str(x) for x in val[0:3]]),
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),
                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'JP'), SimplePathPart('country', no_manip=True)], 'Japan Release Date', 'Japan Release date',
                        transform='JP',
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),

                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'IE'), SimplePathPart('date', no_manip=True)], 'Eire Release Date', 'Eire Release date',
                        transform=lambda val, *args, **kwargs: '-'.join([str(x) for x in val[0:3]]),
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),
                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'IE'), SimplePathPart('country', no_manip=True)], 'Eire Release Date', 'Eire Release date',
                        transform='IE',
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),

                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'BE'), SimplePathPart('date', no_manip=True)], 'Benelux Release Date', 'Benelux Release date',
                        transform=lambda val, *args, **kwargs: '-'.join([str(x) for x in val[0:3]]),
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),
                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'BE'), SimplePathPart('country', no_manip=True)], 'Benelux Release Date', 'Benelux Release date',
                        transform='BE',
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),
                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'NL'), SimplePathPart('date', no_manip=True)], 'Benelux Release Date', 'Benelux Release date',
                        transform=lambda val, *args, **kwargs: '-'.join([str(x) for x in val[0:3]]),
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),
                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'NL'), SimplePathPart('country', no_manip=True)], 'Benelux Release Date', 'Benelux Release date',
                        transform='NL',
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),
                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'LU'), SimplePathPart('date', no_manip=True)], 'Benelux Release Date', 'Benelux Release date',
                        transform=lambda val, *args, **kwargs: '-'.join([str(x) for x in val[0:3]]),
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),
                   both(lambda *args, **kwargs: ['release', 'events', 'combined', (0, 'LU'), SimplePathPart('country', no_manip=True)], 'Benelux Release Date', 'Benelux Release date',
                        transform='LU',
                        condition=lambda val, *args, **kwargs: val != '' and isinstance(val, list)),

                   # XXX: sometimes non-numeric, need to handle this case
                   both(['release', 'barcode'], 'BARCODE', 'Barcode', transform=lambda val, *args, **kwargs: str(int(val)), condition=lambda x, *args, **kwargs: x not in ('', 'N/A')),
                   both(['release', 'tag'], 'MAIN GENRE', 'Main Genre', 'SUB_GENRE', 'Sub_Genre', condition=lambda x, *args, **kwargs: x != ''),

                   both(lambda x, *args, **kwargs: ['release', 'mediums', 'split', 'tracks', (kwargs.get('t_index'),), 'number'], 'TRACK NUMBER', 'track number',
                        prefix=['tracks', ('t_index', True)], suffix=[],
                        transform=lambda val, *args, **kwargs: str(int(val))),
                   both(lambda x, *args, **kwargs: ['release', 'mediums', 'split', 'tracks', (kwargs.get('t_index'),), 'artists', 'split', 'names', (kwargs.get('index'),)], '_ARTIST', '_Artist',
                        prefix=['tracks', ('t_index', True)], suffix=[('index', True, lambda val, *args, **kwargs: val.split('|'))],
                        link=lambda value, *args, **kwargs: 'ninjatune/artist/%s' % value),
                   both(lambda x, *args, **kwargs: ['release', 'mediums', 'split', 'tracks', (kwargs.get('t_index'),), 'artists', 'unsplit'], '_DISPLAY ARTIST', '_Display Artist',
                        prefix=['tracks', ('t_index', True)], suffix=[]),
                   [Rule(['tracks', ('t_index', True)],
                        lambda x, *args, **kwargs: ['release', 'mediums', 'split', 'tracks', (kwargs.get('t_index'),), 'name'],
                        transform=track_name
                    ),
                    Rule(['tracks', ('t_index', True)],
                        lambda x, *args, **kwargs: ['release', 'mediums', 'split', 'tracks', (kwargs.get('t_index'),), 'recording'],
                        transform=track_name,
                        link=lambda value, data, *args, **kwargs: 'ninjatune/release/%s:recording-%s' % (data.get('CATALOGUE NUMBER', data['Catalogue Number'])[0],kwargs.get('t_index')),
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
