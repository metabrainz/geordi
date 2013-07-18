#!/usr/bin/env python2
from __future__ import print_function, division, unicode_literals
from pyelasticsearch import ElasticSearch, ElasticHttpNotFoundError

import sys
import os
import json
import urllib2
import musicbrainzngs

from time import sleep

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../../geordi/geordi'))
from config import ELASTICSEARCH_ENDPOINT, PUBLIC_ENDPOINT

es = ElasticSearch(ELASTICSEARCH_ENDPOINT)
musicbrainzngs.set_useragent('geordi', 'discogs-updater', 'http://geordi.musicbrainz.org')

PUBLIC_ENDPOINT = 'http://geordi.musicbrainz.org'
def initialize():
    # for match in geordi, update
    # for match in MB, update (check if successful; store match if so)
    pass

def update():
    # get existing matches
    # for match in MB, skip and remove from existing match list if exactly the same, otherwise update (store whichever match is most recent after update)
    # for remaining matches in existing, update and store most recent match afterwards [should be unmatches]
    pass

def update_match(itemtype, identifier):
    # ignore artists and labels for now since names are hard
    if itemtype not in ['release', 'master']:
        raise Exception('cannot process this type yet')
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
    return json_data['document']['_source']['_geordi']['matchings']['current_matching'].get('mbid', None)

commands = {'initialize': initialize, 'update': update}
if __name__ == '__main__':
    print(update_match('master', '506527'))
    #command = sys.argv[1]
    #commands[command]()
