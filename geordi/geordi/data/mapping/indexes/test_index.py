from ..rule import Rule
test_index = {
    'album': [
              Rule(['title'],
                   lambda *args, **kwargs: ['release', 'title']),
              Rule(['tracks', ('t_index', lambda a: True), 'title'],
                   lambda *args, **kwargs: ['release','tracks', kwargs.get('t_index'), 'name']),
              Rule(['tracks', ('t_index', lambda a: True), 'duration'],
                   lambda *args, **kwargs: ['release','tracks', kwargs.get('t_index'), 'length'],
                   transform=lambda a, *args, **kwargs: int(a) * 1000),
              Rule(['artists', ('a_index', lambda a: True)],
                   lambda *args, **kwargs: ['release', 'artists', kwargs.get('a_index')],
                   transform=lambda value, *args, **kwargs: {'name': value['name'], 'credit': value.get('credit', value['name'])},
                   link=lambda value, data, *args, **kwargs: 'test_index/artist/%s' % value.get('id'))
              # alternately, remove 'transform' above and use:
              #Rule(['artists', ('a_index', lambda a: True), 'name'],
              #     lambda *args, **kwargs: ['release', 'artists', kwargs.get('a_index'), 'name']),
              #Rule(['artists', ('a_index', lambda a: True), 'credit'],
              #     lambda *args, **kwargs: ['release', 'artists', kwargs.get('a_index'), 'credit']),
             ],
    'artist': [
               Rule(['name'],
                    lambda *args, **kwargs: ['artist', 'name']),
               Rule([('name-lang', lambda key, *args, **kwargs: key[:5] == 'name-')],
                    lambda *args, **kwargs: ['artist', 'aliases'],
                    transform=lambda val, *args, **kwargs: {'name': val, 'locale': kwargs.get('name-lang')[5:]})
              ]
}
