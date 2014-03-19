from ..rule import Rule
test_index = {
    'album': [
              Rule(['title'], ['release', 'name']),
              Rule(['tracks', ('t_index', True), 'title'],
                   lambda *args, **kwargs: ['release','mediums', 'split', 'tracks', (kwargs.get('t_index'),), 'name']),
              Rule(['tracks', ('t_index', True), 'duration'],
                   lambda *args, **kwargs: ['release','mediums', 'split', 'tracks', (kwargs.get('t_index'),), 'length'],
                   transform=lambda a, *args, **kwargs: int(a) * 1000),
              Rule(['artists', ('a_index', True)],
                   lambda *args, **kwargs: ['release', 'artists', 'combined', (kwargs.get('a_index'),)],
                   transform=lambda value, *args, **kwargs: {'name': value['name'], 'credit': value.get('credit', value['name'])},
                   link=lambda value, data, *args, **kwargs: 'test_index/artist/%s' % value.get('id'))
              # alternately, remove 'transform' above and use:
              #Rule(['artists', ('a_index', True), 'name'],
              #     lambda *args, **kwargs: ['release', 'artists', kwargs.get('a_index'), 'name']),
              #Rule(['artists', ('a_index', True), 'credit'],
              #     lambda *args, **kwargs: ['release', 'artists', kwargs.get('a_index'), 'credit']),
             ],
    'artist': [
               Rule(['name'], ['artist', 'name']),
               Rule([('name-lang', lambda key, *args, **kwargs: key[:5] == 'name-')],
                    ['artist', 'aliases'],
                    transform=lambda val, *args, **kwargs: {'name': val, 'locale': kwargs.get('name-lang')[5:]})
              ]
}
