import re
from ..rule import Rule


re_duration = re.compile("PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?")
def transform_duration(text, *args, **kwargs):
    (hours, minutes, seconds) = re_duration.match(text).groups()
    total_seconds = 0

    if hours:
        total_seconds += (int(hours) * 3600)

    if minutes:
        total_seconds += (int(minutes) * 60)

    if seconds:
        total_seconds += int(seconds)

    return total_seconds * 1000


def is_artist_name(display_artist, data, *args, **kwargs):
    return display_artist['ArtistRole']['text'] == 'Artist'


def is_full_credit(display_artist, data, *args, **kwargs):
    return display_artist['ArtistRole']['text'] == 'MainArtist'


def get_artist_name(display_artist, *args, **kwargs):
    return display_artist['PartyName']['FullName']['text']


def get_recording_title(recording, *args, **kwargs):
    return recording['ReferenceTitle']['TitleText']['text']


def is_non_empty(x, *args, **kwargs):
    return x != ''


_genre_fields = ('r', lambda x, *args, **kwargs: x in ('GenreText', 'SubGenre'))


ci_index = {
    'recording': [
        Rule(['ReferenceTitle', 'TitleText', 'text'], ['recording', 'name']),
        Rule(['Duration', 'text'], ['recording', 'length'], transform=transform_duration),
        Rule(['SoundRecordingId', 'ISRC', 'text'], ['recording', 'isrc']),
        Rule(
            ['SoundRecordingDetailsByTerritory', 'DisplayArtist', ('index', True)],
            ['recording', 'artists', 'unsplit'],
            condition=is_full_credit,
            transform=get_artist_name
        ),
        Rule(
            ['SoundRecordingDetailsByTerritory', 'DisplayArtist', ('index', True)],
            ['recording', 'artists', 'split', 'names'],
            condition=is_artist_name,
            transform=get_artist_name
        ),
        Rule(
            ['SoundRecordingDetailsByTerritory', 'Genre', ('index', True), _genre_fields, 'text'],
            ['recording', 'tag'],
            condition=is_non_empty
        )
    ],
    'release': [
        Rule(['ReferenceTitle', 'TitleText', 'text'], ['release', 'name']),
        Rule(['ReleaseId', 'ICPN', 'text'], ['release', 'barcode']),
        Rule(
            ['ReleaseId', 'CatalogNumber', ('index', True), 'text'],
            lambda *args, **kwargs: ['release', 'labels', 'split', 'catalog_numbers', (kwargs.get('index'),)]
        ),
        Rule(
            ['ReleaseDetailsByTerritory', 'LabelName', 'text'],
            ['release', 'labels', 'split', 'labels', (0,)],
        ),
        Rule(
            ['ReleaseResourceReferenceList', 'ReleaseResourceReference', ('t_index', True)],
            lambda *args, **kwargs: ['release', 'mediums', 'split', 'tracks', (kwargs.get('t_index'),), 'recording'],
            transform=lambda value, *args, **kwargs: value['_RecordingName'],
            link=lambda value, data, *args, **kwargs: 'ci/recording/' + value['_ProprietaryId']
        ),
        Rule(
            ['ReleaseResourceReferenceList', 'ReleaseResourceReference', ('t_index', True)],
            lambda *args, **kwargs: ['release', 'mediums', 'split', 'tracks', (kwargs.get('t_index'),), 'length'],
            transform=lambda value, *args, **kwargs: transform_duration(value['_RecordingDuration'])
        ),
        Rule(
            ['ReleaseDetailsByTerritory', 'DisplayArtist', ('index', True)],
            ['release', 'artists', 'unsplit'],
            condition=is_full_credit,
            transform=get_artist_name
        ),
        Rule(
            ['ReleaseDetailsByTerritory', 'DisplayArtist', ('index', True)],
            ['release', 'artists', 'split', 'names'],
            condition=is_artist_name,
            transform=get_artist_name
        ),
        Rule(
            ['ReleaseDetailsByTerritory', 'Genre', ('index', True), _genre_fields, 'text'],
            ['release', 'tag'],
            condition=is_non_empty
        )
    ]
}
