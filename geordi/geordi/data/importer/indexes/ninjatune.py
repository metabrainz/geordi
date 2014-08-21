import xlrd
import json
# First are the "old" spreadsheet, then all the new-style ones.
# No sense bothering to remove the couple of duplicates, I figure.
invariants = ([u'SUB_LABEL', u'MAIN LABEL', u'PRODUCT TITLE', u'PRODUCT VERSION',
               u'ARTIST', u'DISPLAY ARTIST', u'BARCODE', u'CATALOGUE NUMBER',
               u'FORMAT', u'PRICE BAND', u'MAIN RELEASE DATE', u'RIGHTS EXPIRY DATE',
               u'UK RELEASE DATE', u'EIRE RELEASE DATE', u'GERMANY RELEASE DATE',
               u'FRANCE RELEASE DATE', u'BENELUX RELEASE DATE', u'US RELEASE DATE',
               u'AUSTRALIA RELEASE DATE', u'JAPAN RELEASE DATE',
               u'_P_ YEAR', u'_P_ HOLDER',
               u'_C_ YEAR', u'_C_ HOLDER', u'MAIN GENRE', u'SUB_GENRE',
               u'TERRITORIES _ ZONES INCLUDED', u'TERRITORIES _ ZONES EXCLUDED',
               u'PART NUMBER', u'TOTAL PARTS'] +
              [u'Sub_Label', u'Main Label', u'Product Title',
               u'Product Version', u'Artist', u'Display Artist', u'Barcode',
               u'Master Release', u'Catalogue Number', u'Format', u'Price Band',
               u'Main Release Date', u'Rights Expiry Date', u'UK Release Date',
               u'Eire Release Date', u'Germany Release Date',
               u'France Release date', u'Benelux Release date',
               u'US Release Date', u'Australia Release date',
               u'Japan Release date', u'_P_ YEAR', u'_P_ HOLDER', u'_C_ YEAR',
               u'_C_ HOLDER', u'Main Genre', u'Sub_Genre',
               u'Territories _ Zones Included', u'Territories _ Zones Excluded',
               u'Part Number', u'Total Parts'])

known_fields = (invariants +
                [u'TRACK NUMBER', u'MAIN TITLE', u'TITLE VERSION', u'_ARTIST',
                 u'_DISPLAY ARTIST', u'ISRC CODE', u'_MAIN GENRE',
                 u'_SUB_GENRE', u'__P_ YEAR', u'__P_ HOLDER', u'__C_ YEAR',
                 u'__C_ HOLDER', u'PUBLISHER', u'COMPOSER', u'LYRICIST',
                 u'PRODUCER', u'MIXER', u'EXPLICIT LYRICS?',
                 u'CAN TRACK BE MADE AVAILABLE INDIVIDUALLY?', u'DURATION',
                 u'ENTRY NUMBER', u'RINGTONE TYPE', u'TO', u'KEYWORD', u'NUMBER',
                 u'PREVIEW URL'] +
                [u'track number', u'Main Title', u'Title Version', u'_Artist',
                 u'_Display Artist', u'ISRC Code', u'_Main Genre',
                 u'_Sub_Genre', u'__P_ Year', u'__P_ Holder', u'__C_ Year',
                 u'__C_ Holder', u'Publisher', u'Composer', u'Lyricist',
                 u'Producer', u'Mixer', u'Explicit Lyrics?',
                 u'Can track be made available individually?', u'Ringtone Type',
                 u'Keyword', u'Number', u'To', u'Preview URL',
                 u'Physical FileName', u'SampleFile', u'Entry Number', u'BPM',
                 u'USED IN ROYALTIES', u'Duration'])

def track_sort(track):
    for key_field in [u'TRACK NUMBER', u'track number']:
        if key_field in track:
            try:
                return int(track[key_field])
            except Exception:
                return track[key_field]
    return None

def ninjatune_setup(add_folder, add_data_item, import_manager):
    @import_manager.command
    def ninjatune(xls_file):
        '''Import ninjatune data provided in a .xls file.'''
        book = xlrd.open_workbook(xls_file)
        sh = book.sheet_by_index(0)
        headers = [cell.value for cell in sh.row(0)]
        for i in range(0, len(headers)):
            if headers[i] == '':
                headers[i] = 'column:' + str(i)
            elif headers[i] not in known_fields:
                raise Exception('Unknown header column %s' % headers[i])
        data = {}
        for row_number in range(1,sh.nrows):
            row = sh.row(row_number)
            key = None
            for key_field in [u'CATALOGUE NUMBER', u'Catalogue Number']:
                if key_field in headers:
                    key = row[headers.index(key_field)].value
                    break;
            if key is None:
                raise Exception('Couldn\'t figure out what to use as a key for this file.')
            if key == '':
                continue # empty catalogue number field
            data[key] = data.get(key, {})
            this_track = {}
            for cell_number in range(0, len(row)):
                cell_key = headers[cell_number]
                # Fix dates to tuple/array format. ctype 3 is XL_CELL_DATE
                if row[cell_number].ctype == 3:
                    cell_value = xlrd.xldate_as_tuple(row[cell_number].value, book.datemode)
                else:
                    cell_value = row[cell_number].value
                if cell_key in invariants:
                    data[key][cell_key] = data[key].get(cell_key, [])
                    if cell_value not in data[key][cell_key]:
                        data[key][cell_key].append(cell_value)
                else:
                    this_track[cell_key] = cell_value
            data[key]['tracks'] = sorted(data[key].get('tracks', []) + [this_track], key=track_sort)
        for (key, item_data) in data.iteritems():
            data_id = 'ninjatune/release/' + key
            print add_data_item(data_id, 'release', json.dumps(item_data, separators=(',', ':'), sort_keys=True))
