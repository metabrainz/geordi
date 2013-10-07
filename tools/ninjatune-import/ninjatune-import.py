#!/usr/bin/env python
# Roughly speaking:
# release level fields: SUB_LABEL,MAIN LABEL,PRODUCT TITLE,PRODUCT VERSION,ARTIST,DISPLAY ARTIST,BARCODE,CATALOGUE NUMBER,
#                        FORMAT,MAIN RELEASE DATE,_P_ YEAR,_P_ HOLDER,_C_ YEAR,_C_ HOLDER,MAIN GENRE,SUB_GENRE,
#                        TERRITORIES _ ZONES INCLUDED,TERRITORIES _ ZONES EXCLUDED,PART NUMBER,TOTAL PARTS,
#                        MAIN TITLE,_ARTIST,_DISPLAY ARTIST, _MAIN GENRE,_SUB_GENRE,__P_ YEAR,__P_ HOLDER,__C_ YEAR,
#                        __C_ HOLDER,PUBLISHER,unlabeled_1,unlabeled_2,unlabeled_3,unlabeled_4,unlabeled_5,
#                        unlabeled_6,unlabeled_7,unlabeled_8,unlabeled_9,unlabeled_10,unlabeled_11,unlabeled_12,unlabeled_13
# recording level fields: TRACK NUMBER,MAIN TITLE,TITLE VERSION,ISRC CODE,unlabeled_0,unlabeled_10

import sys
import csv
import json
import codecs

if len(sys.argv) < 2:
    print "Usage: %s <ninjatune csv file>" % (sys.argv[0])
    sys.exit(-1)

releases = []

try:
    with open(sys.argv[1], 'rbU') as csvfile:
        reader = csv.reader(csvfile)

        last_catno = u""
        tracks = []
        prev = {}
        for i, utf8_row in enumerate(reader):

            # Read a row and convert it to unicode
            row = []
            for x in utf8_row:
                row.append(unicode(x.decode('utf-8')))
            if i == 0:
                columns = row
                continue

            data = {} 
            for j, col in enumerate(row):
                data[columns[j]] = col

            # Make sure we have a catalog number, even if its a dummy one
            try:
                dummy = data['CATALOGUE NUMBER']
            except KeyError:
                data['CATALOGUE NUMBER'] = u"-- no catno --"

            # If the catalog number has changed, assume that we're onto the next release
            # and process the previous set of tracks
            if data['CATALOGUE NUMBER'] != last_catno and last_catno:
                variant_cols = []
                invariant_cols = []
                invariant_data = {}
                invariant = True

                # iterate over the columns looking for variant or invarant data
                for col in columns:
                    for track in tracks[1:]:
                        if track[col] != tracks[0][col]:
                            invariant = False
                            break

                    # tuck the data away accordingly
                    if invariant:
                        invariant_cols.append(col)

                        # I believe this case handles single track releases, but I am not 100%.
                        # I'm too hopped up on cold meds to recall. :(
                        try:
                            invariant_data[col] = tracks[0][col]
                        except KeyError:
                            invariant_data[col] = u""
                    else:
                        variant_cols.append(col)

                # based on our collected data, cobble together a release
                track_data = []
                for track in tracks:
                    variant_data = {}
                    for col in variant_cols:
                        if track[col]: variant_data[col] = track[col]

                    track_data.append(variant_data)

                release = invariant_data
                release['tracks'] = track_data
                releases.append(release)

                tracks = []

            # if the data is just another track on the same release (with the same catalog number)
            # save it and move on.
            tracks.append(data)
            prev = data
            last_catno = data['CATALOGUE NUMBER']

        # We're done! Dump the data and be done
        dumps = json.dumps({ 'ninjatune' : releases }, sort_keys=True, indent=4, ensure_ascii=False)
        print dumps.encode('utf-8')
except IOError:
    print "Cannot open %s. You fail." % sys.argv[1]
