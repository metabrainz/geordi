#!/usr/bin/env python2
from __future__ import print_function, division, unicode_literals
from pyelasticsearch import ElasticSearch, ElasticHttpNotFoundError

import sys
import os
import json
import urllib2

from time import sleep

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../../geordi/geordi'))
from config import ELASTICSEARCH_ENDPOINT, PUBLIC_ENDPOINT

es = ElasticSearch(ELASTICSEARCH_ENDPOINT)

PUBLIC_ENDPOINT = 'http://geordi.musicbrainz.org'
def initialize():
    # for match in geordi, update
    stored_data = []
    existing_matches = []
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
    mb_matches = []
    for match in mb_matches:
        # resolve name here, if appropriate
        data = update_match(match['itemtype'], match['id'])
        if data[2] is not None:
            stored_data.append(data)

    # for remaining matches in existing, update and store most recent match afterwards [should be unmatches]

    store_data(stored_data)

def store_data(stored_data):
    pass

def get_stored_data():
    pass

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
    sleep(1)
    # then a fetch
    json_data = json.load(urllib2.urlopen(url))
    mbids = json_data['document']['_source']['_geordi']['matchings']['current_matching'].get('mbid', None)
    if itemtype not in ['release', 'master']:
        return (itemtype, identifier, mbids, json_data['document']['_source']['name'])
    else:
        return (itemtype, identifier, mbids)

commands = {'initialize': initialize, 'update': update}
if __name__ == '__main__':
    print(update_match('master', '506527'))
    #command = sys.argv[1]
    #commands[command]()
