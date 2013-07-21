#!/usr/bin/env python2
from __future__ import print_function, division, unicode_literals
from pyelasticsearch import ElasticSearch, ElasticHttpNotFoundError

import sys
import os
import json
import urllib
import urllib2

from time import sleep

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../../geordi/geordi'))
from config import ELASTICSEARCH_ENDPOINT, PUBLIC_ENDPOINT

es = ElasticSearch(ELASTICSEARCH_ENDPOINT)

DATA_FILE = './data.json'
MB_FILE = './mb-data.tsv'

PUBLIC_ENDPOINT = 'http://geordi.musicbrainz.org'
def initialize():
    # for match in geordi, update
    stored_data = []
    existing_matches = get_from_elasticsearch()
    for match in existing_matches:
        data = update_match(match['itemtype'], match['id'])
        if data[2] is not None:
            stored_data.append(data)

    store_data(stored_data)

    # for match in MB, update (store most recent match after update)
    update()

def update():
    # get existing matches
    existing = get_stored_data()
    # for match in MB, skip and remove from existing match list if exactly the same, otherwise update (store whichever match is most recent after update)
    stored_data = []
    mb_matches = get_from_mb()
    count = 0
    for match in mb_matches:
        count = count + 1
        if count % 50 == 0:
            print('Storing data...')
            store_data(stored_data)
        match['name'] = urllib.unquote_plus(str(match['name'])).decode('utf-8')
        if match['itemtype'] not in ['release', 'master']:
            key = match['itemtype'] + ':' + match['name']
        else:
            key = match['itemtype'] + ':' + match['id']

        print('Doing ' + key)
        if existing.get(key, False):
            if ','.join(match['mbids']) == ','.join(existing[key][2]):
                print('> Already done.')
                stored_data.append(existing[key])
            else:
                print('> MBIDs differ, updating.')
                data = update_match(existing[key][0], existing[key][1])
                if data[2] is not None:
                    print('>> Updated to ' + repr(data[2]))
                    stored_data.append(data)
                else:
                    print('>> No match registered.')
            del existing[key]
        else:
            print('> No record, resolving name.')
            try:
                if match['itemtype'] not in ['release', 'master']:
                    match['id'] = get_id(match['itemtype'], match['name'])
                print('>> Found name ' + match['name'] + ' maps to id ' + match['id'])
                data = update_match(match['itemtype'], match['id'])
                if data[2] is not None:
                    print('>> Updated to ' + repr(data[2]))
                    stored_data.append(data)
                else:
                    print('>> No match registered.')
            except Exception:
                print('>> Name not found in geordi. Skipping.')
                continue

    # for remaining matches in existing, update and store most recent match afterwards [should be unmatches]
    for (key, match) in existing.iteritems():
        data = update_match(match[0], match[1])
        if data[2] is not None:
            stored_data.append(data)

    store_data(stored_data)

def get_id(itemtype, name):
    url = PUBLIC_ENDPOINT + '/api/search'
    query = u'_id:%s-* and name:"%s"' % (itemtype, name.replace('"', '\\"'))
    query = query.encode('utf-8')
    url_data = urllib.urlencode({'type': 'query',
            'query': query,
            'index': 'discogs',
            'itemtype': 'subitem'})

    data = json.load(urllib2.urlopen(url + '?' + url_data))
    for result in data['result']['hits']['hits']:
        try:
            geordi_name = result['_source']['name']
            entity_id = result['_id'].split('-')[1]
            if name in geordi_name:
                return entity_id
            else:
                continue
        except Exception, e:
            continue
    raise Exception('Name doesn\'t match in any result')

def get_from_mb():
    mbdata = []
    fh = open(MB_FILE, 'r')
    for line in fh.readlines():
        # Format is <type>\t<ID, parsed from URL>\t<MBIDs, comma-separated>
        (itemtype, identifier, mbid_string) = line[:-1].split('\t')
        mbids = mbid_string.split(',')

        if itemtype not in ['release', 'master']:
            mbdata.append({'itemtype': itemtype, 'name': identifier, 'mbids': mbids})
        else:
            mbdata.append({'itemtype': itemtype, 'id': identifier, 'mbids': mbids})
    fh.close()
    return mbdata

def get_from_elasticsearch():
    return []

def store_data(stored_data):
    store_dict = {}
    for entry in stored_data:
        if entry[0] not in ['release', 'master']:
            key = entry[0] + ':' + entry[3][0]
        else:
            key = entry[0] + ':' + entry[1]
        store_dict[key] = entry
    fh = open(DATA_FILE, 'w')
    fh.write(json.dumps(store_dict))
    fh.close()

def get_stored_data():
    try:
        fh = open(DATA_FILE, 'r')
        data = json.load(fh)
        fh.close()
        return data
    except Exception:
        return {}

def update_match(itemtype, identifier):
    # We're assuming you're passing a real ID number, not a name.
    if itemtype == 'release':
        geordi_type = 'item'
        geordi_identifier = identifier
    else:
        geordi_type = 'subitem'
        geordi_identifier = itemtype + '-' + identifier
    url = PUBLIC_ENDPOINT + '/api/' + geordi_type + '/discogs/' + geordi_identifier + '?update=1'
    # first an update
    urllib2.urlopen(url)
    # then a fetch
    json_data = json.load(urllib2.urlopen(url))
    mbids = json_data['document']['_source']['_geordi']['matchings']['current_matching'].get('mbid', None)
    if itemtype not in ['release', 'master']:
        return (itemtype, identifier, mbids, json_data['document']['_source']['name'])
    else:
        return (itemtype, identifier, mbids)

commands = {'initialize': initialize, 'update': update}
if __name__ == '__main__':
    command = sys.argv[1]
    commands[command]()
