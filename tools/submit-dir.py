#!/usr/bin/env python2
from __future__ import print_function, division, unicode_literals
from pyelasticsearch import ElasticSearch, ElasticHttpNotFoundError

import sys
import re
import os

import xmltodict
import json
import copy

xmltodict.OrderedDict = dict
es = ElasticSearch('http://localhost:9200')

def process_dir(index, directory):
    base = re.sub('(.*?)/([^/]+)/?$', r'\2', directory)
    print('processing {}...'.format(base))
    try:
        document = es.get(index, 'item', base)
        doc = document["_source"]
        version = document["_version"]
    except ElasticHttpNotFoundError:
        doc = {}
        version = None

    new_data = read_directory(directory, base)
    new_doc = copy.deepcopy(doc)
    new_doc.update(new_data)

    # Reset mapping, as this data may have changed
    # Links always check if there's really been changes
    if '_geordi' in new_doc:
        new_doc['_geordi']['mapping'] = {'version': 0}

    if version:
        es.index(index, 'item', new_doc, id=base, es_version=version)
    else:
        es.index(index, 'item', new_doc, id=base)

def read_directory(directory, base):
    data = {}
    for filename in os.listdir(directory):
        filebase = re.sub(r'\.', '_',
                      re.sub(r'^[\s_-]+|[\s_-]+$', '',
                      filename.replace(base, '')))
        with open(directory + '/' + filename) as fh:
            content = fh.read()
        if re.search(r'\.xml$', filename):
            processed = process_xml(content)
        elif re.search(r'\.json$', filename):
            processed = process_json(content)
        else:
            processed = content

        if processed:
            data[filebase] = processed
    return data

def process_xml(content):
    try:
        return xmltodict.parse(content, force_cdata=True, attr_prefix='_', cdata_key='text')
    except:
        return None

def process_json(content):
    try:
        return json.loads(content)
    except:
        return None

if __name__ == '__main__':
    index = sys.argv[1]
    directories = sys.argv[2:]
    for directory in directories:
        try:
            process_dir(index, directory)
        except Exception, e:
            print("GOT EXCEPTION: {}".format(e))
            continue
